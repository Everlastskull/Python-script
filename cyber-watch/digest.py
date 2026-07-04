"""Construit et envoie le digest email quotidien de veille cyber : un flux RSS/API
minimal (bibliothèque standard, cf. commentaire plus bas) complété par du scraping
best-effort (scraper.py) pour les sources sans flux exploitable.
"""

import email.utils
import html
import json
import os
import re
import smtplib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import scraper
import state
from feeds import FEEDS, MANUAL_ONLY

LOOKBACK_HOURS = int(os.environ.get("DIGEST_LOOKBACK_HOURS", "24"))
REQUEST_TIMEOUT = 15
NETWORK_RETRIES = 2
RETRY_DELAY_SECONDS = 3
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# Se présenter comme un vrai lecteur RSS : certains sites (CERT-FR, CISA...)
# renvoient une réponse vide ou un 403 aux clients HTTP non identifiés.
# feedparser n'est volontairement pas utilisé : sa dépendance sgmllib3k ne se
# build plus avec les versions récentes de setuptools. On parse donc le
# RSS/Atom nous-mêmes avec xml.etree.
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; cyber-watch-digest/1.0; +https://github.com/Everlastskull/Python-script)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
}
# Répare les esperluettes non échappées, fréquentes dans les flux mal générés
# (ex: Sekoia), qui font échouer un parseur XML strict.
_BARE_AMPERSAND = re.compile(rb"&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9a-fA-F]+);)")

CATEGORY_COLORS = {
    "GRC / Réglementaire": "#2563eb",
    "Threat Intelligence": "#dc2626",
    "OT / ICS / SCADA": "#ea580c",
    "CVE / Offensif": "#7c3aed",
}
DEFAULT_COLOR = "#4b5563"


def sanitize_xml(data):
    return _BARE_AMPERSAND.sub(b"&amp;", data)


def strip_ns(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def parse_date(raw):
    if not raw:
        return None
    try:
        return email.utils.parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def child_text(element, name):
    for child in element:
        if strip_ns(child.tag) == name:
            return (child.text or "").strip()
    return ""


def atom_link(element):
    for child in element:
        if strip_ns(child.tag) == "link":
            href = child.get("href")
            if href and child.get("rel") in (None, "alternate"):
                return href
    return ""


def parse_entries(xml_bytes):
    root = ET.fromstring(xml_bytes)
    items = []

    channel = None
    for child in root:
        if strip_ns(child.tag) == "channel":
            channel = child
            break

    if channel is not None:
        # RSS 2.0
        for item in channel:
            if strip_ns(item.tag) != "item":
                continue
            title = child_text(item, "title")
            link = child_text(item, "link")
            published = parse_date(child_text(item, "pubDate"))
            items.append((title, link, published))
    else:
        # Atom
        for entry in root:
            if strip_ns(entry.tag) != "entry":
                continue
            title = child_text(entry, "title")
            link = atom_link(entry)
            published = parse_date(child_text(entry, "published") or child_text(entry, "updated"))
            items.append((title, link, published))

    return items


def fetch_with_retry(url):
    """Récupère l'URL, en ré-essayant seulement les erreurs réseau transitoires
    (timeout, DNS, connexion). Les erreurs HTTP (403/404...) sont définitives :
    inutile de les ré-essayer."""
    request = urllib.request.Request(url, headers=REQUEST_HEADERS)
    last_error = None
    for attempt in range(NETWORK_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                return response.read(), None
        except urllib.error.HTTPError as exc:
            return None, f"HTTP {exc.code}"
        except Exception as exc:  # noqa: BLE001 - un flux en erreur ne doit pas casser les autres
            last_error = str(exc)
            if attempt < NETWORK_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
    return None, last_error


def fetch_recent_entries(url, cutoff):
    data, error = fetch_with_retry(url)
    if error:
        return [], error

    if not data.strip():
        return [], "réponse vide"

    try:
        entries = parse_entries(data)
    except ET.ParseError:
        try:
            entries = parse_entries(sanitize_xml(data))
        except ET.ParseError as exc:
            return [], f"flux illisible ({exc})"

    recent = [
        (title, link)
        for title, link, published in entries
        if published is None or published >= cutoff
    ]
    return recent, None


def fetch_nvd_recent(cutoff):
    """NVD a retiré ses flux RSS au profit de l'API 2.0 (gratuite, sans clé,
    voir https://nvd.nist.gov/general/news/api-20-announcements)."""
    now = datetime.now(timezone.utc)
    params = {
        "pubStartDate": cutoff.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "pubEndDate": now.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "resultsPerPage": "20",
    }
    url = f"{NVD_API_URL}?{urllib.parse.urlencode(params)}"
    data, error = fetch_with_retry(url)
    if error:
        return [], error

    try:
        payload = json.loads(data)
    except json.JSONDecodeError as exc:
        return [], f"réponse illisible ({exc})"

    entries = []
    for item in payload.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id", "?")
        description = next(
            (d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"),
            "",
        )
        title = f"{cve_id} — {description[:140]}" if description else cve_id
        link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
        entries.append((title, link))
    return entries, None


API_SOURCES = {
    "CVE / Offensif": [("NVD – CVE récents (API)", fetch_nvd_recent)],
}


def collect_report():
    """Interroge RSS + API + scraping, dédoublonne le scraping via l'état
    persistant, et renvoie (report, new_seen_urls).

    report: {catégorie: [(nom_source, [(titre, lien), ...], erreur_ou_None)]}
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    report = {category: [] for category in FEEDS}

    for category, sources in FEEDS.items():
        for name, url in sources:
            entries, error = fetch_recent_entries(url, cutoff)
            report[category].append((name, entries, error))
        for name, fetch_api in API_SOURCES.get(category, []):
            entries, error = fetch_api(cutoff)
            report[category].append((name, entries, error))

    seen = set(state.load_seen())
    new_seen = list(state.load_seen())
    try:
        scrape_results = scraper.scrape_all()
    except Exception as exc:  # noqa: BLE001 - le scraping ne doit pas casser le reste du digest
        scrape_results = {}
        report.setdefault("Threat Intelligence", []).append(
            ("Scraping (navigateur headless)", [], f"échec global : {exc}")
        )

    for category, sources in scrape_results.items():
        report.setdefault(category, [])
        for name, articles, error in sources:
            if error:
                report[category].append((name, [], error))
                continue
            fresh = [(title, link) for title, link in articles if link not in seen]
            for _, link in fresh:
                seen.add(link)
                new_seen.append(link)
            report[category].append((name, fresh, None))

    return report, new_seen


def render_text(report):
    header = (
        f"VEILLE CYBER QUOTIDIENNE — par Matthieu Maurial\n"
        f"{datetime.now().strftime('%d/%m/%Y')} · dernières 24 h\n"
    )
    sections = [header]
    for category, sources in report.items():
        lines = []
        for name, entries, error in sources:
            if error:
                lines.append(f"  - {name}: indisponible ({error})")
                continue
            if not entries:
                continue
            lines.append(f"  - {name}:")
            for title, link in entries:
                lines.append(f"      * {title}\n        {link}")
        if lines:
            sections.append(f"{category}\n" + "\n".join(lines))

    if MANUAL_ONLY:
        manual = "\n".join(f"  - {name}" for name in MANUAL_ONLY)
        sections.append("À consulter manuellement (pas de flux/API exploitable)\n" + manual)

    return "\n\n".join(sections)


def render_html(report):
    date_str = datetime.now().strftime("%d/%m/%Y")
    cards = []

    for category, sources in report.items():
        color = CATEGORY_COLORS.get(category, DEFAULT_COLOR)
        body_parts = []
        has_content = False

        for name, entries, error in sources:
            safe_name = html.escape(name)
            if error:
                body_parts.append(
                    f'<div style="font-size:12px;color:#9ca3af;margin-bottom:8px;">'
                    f'{safe_name} : indisponible ({html.escape(error)})</div>'
                )
                continue
            if not entries:
                continue
            has_content = True
            items_html = "".join(
                f'<li style="margin-bottom:6px;line-height:1.4;">'
                f'<a href="{html.escape(link)}" style="color:{color};text-decoration:none;">'
                f'{html.escape(title)}</a></li>'
                for title, link in entries
            )
            body_parts.append(
                f'<div style="margin-bottom:12px;">'
                f'<div style="font-weight:600;color:#111827;font-size:13px;margin-bottom:4px;">{safe_name}</div>'
                f'<ul style="margin:0;padding-left:18px;">{items_html}</ul>'
                f"</div>"
            )

        if not body_parts:
            continue

        badge = (
            f'<span style="background:#16a34a;color:#fff;font-size:10px;'
            f'padding:2px 8px;border-radius:10px;margin-left:8px;">nouveau</span>'
            if has_content
            else ""
        )
        cards.append(
            f'<div style="border:1px solid #e5e7eb;border-radius:10px;margin-bottom:16px;overflow:hidden;">'
            f'<div style="background:{color};color:#fff;padding:10px 16px;font-weight:600;font-size:14px;">'
            f"{html.escape(category)}{badge}</div>"
            f'<div style="padding:14px 16px;background:#ffffff;">{"".join(body_parts)}</div>'
            f"</div>"
        )

    manual_html = "".join(
        f'<div style="margin-bottom:2px;">• {html.escape(name)}</div>' for name in MANUAL_ONLY
    )

    return f"""\
<div style="font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;max-width:640px;margin:0 auto;background:#f3f4f6;padding:24px;">
  <div style="text-align:center;margin-bottom:24px;">
    <div style="font-size:22px;font-weight:700;color:#111827;">🛡️ Veille Cyber Quotidienne</div>
    <div style="font-size:13px;color:#6b7280;margin-top:2px;">par Matthieu Maurial</div>
    <div style="font-size:12px;color:#9ca3af;margin-top:4px;">{date_str} · dernières 24 h</div>
  </div>
  {"".join(cards) if cards else '<div style="text-align:center;color:#6b7280;font-size:13px;">Aucun nouvel article dans la fenêtre de veille.</div>'}
  <div style="border-top:1px solid #d1d5db;margin-top:20px;padding-top:14px;font-size:11px;color:#9ca3af;">
    <strong>À consulter manuellement</strong> (pas de flux/API exploitable) :
    <div style="margin-top:6px;">{manual_html}</div>
  </div>
</div>
"""


def send_email(text_body, html_body):
    smtp_user = os.environ["GMAIL_USER"]
    smtp_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["DIGEST_TO"]

    message = MIMEMultipart("alternative")
    message["From"] = smtp_user
    message["To"] = recipient
    message["Subject"] = f"Veille Cyber Quotidienne — {datetime.now().strftime('%Y-%m-%d')}"
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient, message.as_string())


def main():
    report, new_seen = collect_report()
    send_email(render_text(report), render_html(report))
    state.save_seen(new_seen)
    print("Digest envoyé.")


if __name__ == "__main__":
    sys.exit(main())
