"""Envoie un digest email quotidien des derniers articles des flux de veille cyber.

Parseur RSS/Atom minimal en bibliothèque standard uniquement (pas de dépendance
externe : feedparser tire sgmllib3k, qui ne se build plus avec les versions
récentes de setuptools).
"""

import email.utils
import os
import smtplib
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from feeds import FEEDS

LOOKBACK_HOURS = int(os.environ.get("DIGEST_LOOKBACK_HOURS", "24"))
REQUEST_TIMEOUT = 15
USER_AGENT = "cyber-watch-digest/1.0 (+https://github.com/Everlastskull/Python-script)"


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


def fetch_recent_entries(url, cutoff):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            data = response.read()
    except Exception as exc:  # noqa: BLE001 - un flux en erreur ne doit pas casser les autres
        return [], str(exc)

    try:
        entries = parse_entries(data)
    except ET.ParseError as exc:
        return [], f"flux illisible ({exc})"

    recent = [
        (title, link)
        for title, link, published in entries
        if published is None or published >= cutoff
    ]
    return recent, None


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
        if lines:
            sections.append(f"{category}\n" + "\n".join(lines))

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
