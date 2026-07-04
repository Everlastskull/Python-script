"""Scraping best-effort (navigateur headless) pour les sources sans flux RSS/API
exploitable, ou protégées par un anti-bot léger (Cloudflare "Bot Fight Mode").

Aucune garantie de contournement pour les protections plus dures (Akamai, JS
challenge géré) — notamment sur les sites gouvernementaux (CISA). Si un run réel
remonte 0 résultat pour une source qui en a manifestement, les sélecteurs/URL
ci-dessous doivent être ajustés en conséquence.
"""

from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
NAV_TIMEOUT_MS = 30000
STEALTH_INIT_SCRIPT = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
MIN_TEXT_LENGTH = 15
MAX_ARTICLES_PER_SOURCE = 8
EXCLUDED_SLUGS = {
    "tag", "tags", "author", "authors", "page", "category", "categories",
    "about", "contact", "rss", "feed", "search", "login", "subscribe",
}


def contains_any(*substrings):
    def predicate(href):
        return any(s in href for s in substrings)
    return predicate


def path_depth_one(host):
    def predicate(href):
        parsed = urlparse(href)
        if parsed.netloc != host:
            return False
        segments = [s for s in parsed.path.split("/") if s]
        return len(segments) == 1 and segments[0].lower() not in EXCLUDED_SLUGS
    return predicate


SCRAPE_TARGETS = {
    "GRC / Réglementaire": [
        ("CERT-FR – Avis", "https://www.cert.ssi.gouv.fr/avis/", contains_any("/avis/CERTFR-")),
        ("CERT-FR – Alertes", "https://www.cert.ssi.gouv.fr/alerte/", contains_any("/alerte/CERTFR-")),
        ("CERT-FR – Bulletins d'actualité", "https://www.cert.ssi.gouv.fr/actualite/", contains_any("/actualite/CERTFR-")),
    ],
    "Threat Intelligence": [
        ("Recorded Future Blog", "https://www.recordedfuture.com/blog", contains_any("/blog/")),
        ("Sekoia.io Blog", "https://blog.sekoia.io/", path_depth_one("blog.sekoia.io")),
        ("Dragos Blog", "https://www.dragos.com/blog/", contains_any("/blog/")),
    ],
    "OT / ICS / SCADA": [
        ("CISA ICS Advisories", "https://www.cisa.gov/news-events/ics-advisories", contains_any("/ics-advisories/icsa-", "/ics-advisories/icsma-")),
    ],
}


def _extract_links(page, predicate):
    raw_links = page.eval_on_selector_all(
        "a[href]",
        "els => els.map(e => ({href: e.href, text: e.innerText.trim()}))",
    )
    seen_urls = set()
    articles = []
    for link in raw_links:
        href = link.get("href", "")
        text = link.get("text", "")
        if len(text) < MIN_TEXT_LENGTH:
            continue
        if not predicate(href):
            continue
        if href in seen_urls:
            continue
        seen_urls.add(href)
        articles.append((text, href))
        if len(articles) >= MAX_ARTICLES_PER_SOURCE:
            break
    return articles


def scrape_all():
    """Retourne {catégorie: [(nom_source, [(titre, lien), ...], erreur_ou_None)]}."""
    results = {category: [] for category in SCRAPE_TARGETS}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 900},
        )
        context.add_init_script(STEALTH_INIT_SCRIPT)
        page = context.new_page()

        for category, targets in SCRAPE_TARGETS.items():
            for name, url, predicate in targets:
                try:
                    page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
                    articles = _extract_links(page, predicate)
                    results[category].append((name, articles, None))
                except Exception as exc:  # noqa: BLE001 - une source en erreur ne doit pas casser les autres
                    results[category].append((name, [], str(exc)))

        browser.close()
    return results
