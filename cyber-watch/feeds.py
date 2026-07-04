"""Liste des flux RSS de veille, groupés par catégorie (cf. README.md).

Les sources sans flux RSS/API exploitable, ou protégées par un anti-bot léger,
sont tentées via scraping navigateur (voir scraper.py). Ce qui reste ici dans
MANUAL_ONLY n'a ni flux, ni API, ni page listant les articles de façon fiable.
"""

FEEDS = {
    "GRC / Réglementaire": [
        ("ANSSI – Actualités", "https://cyber.gouv.fr/actualites/rss/"),
    ],
    "Threat Intelligence": [
        ("Bleeping Computer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ],
    "OT / ICS / SCADA": [
        ("S4x Events Blog", "https://s4xevents.com/feed/"),
    ],
    "CVE / Offensif": [
        ("Exploit-DB", "https://www.exploit-db.com/rss.xml"),
        ("Project Zero – Google", "https://googleprojectzero.blogspot.com/feeds/posts/default"),
    ],
}

# Ni flux RSS, ni API gratuite exploitable, ni page de liste stable à scraper :
# ENISA (RSS discontinué, pas de remplacement), Legifrance et AttackerKB (API
# gratuites mais nécessitant un compte personnel, non configuré), Claroty
# Team82 et Mandiant/Google Cloud (pas de flux ni d'API publique trouvée).
MANUAL_ONLY = [
    "ENISA",
    "Legifrance (API disponible via piste.gouv.fr, compte non configuré)",
    "Claroty Team82",
    "AttackerKB (API disponible, compte non configuré)",
    "Mandiant / Google Cloud Threat Intelligence",
]
