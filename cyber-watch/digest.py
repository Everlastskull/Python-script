"""Envoie un digest email quotidien des derniers articles des flux de veille cyber.

Parseur RSS/Atom minimal en bibliothèque standard uniquement (pas de dépendance
externe : feedparser tire sgmllib3k, qui ne se build plus avec les versions
récentes de setuptools).
"""

import email.utils
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

from feeds import FEEDS, MANUAL_ONLY

LOOKBACK_HOURS = int(os.environ.get("DIGEST_LOOKBACK_HOURS", "24"))
REQUEST_TIMEOUT = 15
NETWORK_RETRIES = 2
RETRY_DELAY_SECONDS = 3
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
# Se présenter comme un vrai lecteur RSS : certains sites (CERT-FR, CISA...)
# renvoient une réponse vide ou un 403 aux clients HTTP non identifiés.
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; cyber-watch-digest/1.0; +https://github.com/Everlastskull/Python-script)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
}
# Répare les esperluettes non échappées, fréquentes dans les flux mal générés
# (ex: Sekoia), qui font échouer un parseur XML strict.
_BARE_AMPERSAND = re.compile(rb"&(?!(?:[a-zA-Z][a-zA-Z0-9]*|#\d+|#x[0-9a-fA-F]+);)")


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


def build_digest():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    sections = []
    for category, sources in FEEDS.items():
        lines = []
        for name, url in sources:
            entries, error = fetch_recent_entries(url, cutoff)
            if error:
                lines.append(f"  - {name}: indisponible ({error})")
                continue
            if not entries:
                continue
            lines.append(f"  - {name}:")
            for title, link in entries:
                lines.append(f"      * {title}\n        {link}")
        for name, fetch_api in API_SOURCES.get(category, []):
            entries, error = fetch_api(cutoff)
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
        sections.append(
            "À consulter manuellement (pas de flux RSS exploitable automatiquement)\n" + manual
        )

    if not sections:
        return None
    return "\n\n".join(sections)


def send_email(body):
    smtp_user = os.environ["GMAIL_USER"]
    smtp_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["DIGEST_TO"]

    message = MIMEMultipart()
    message["From"] = smtp_user
    message["To"] = recipient
    message["Subject"] = f"Cyber Watch — Digest du {datetime.now().strftime('%Y-%m-%d')}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient, message.as_string())


def main():
    body = build_digest()
    if body is None:
        print("Aucun nouvel article dans la fenêtre de veille, pas d'email envoyé.")
        return
    send_email(body)
    print("Digest envoyé.")


if __name__ == "__main__":
    sys.exit(main())
