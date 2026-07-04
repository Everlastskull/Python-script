"""Liste des flux RSS de veille, groupés par catégorie (cf. README.md)."""

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

# Sources bloquées par une protection anti-bot (Cloudflare "Bot Fight Mode" ou
# équivalent côté gouvernemental) qui renvoie un défi JavaScript ou une réponse
# vide aux clients scriptés — y compris depuis les runners GitHub Actions.
# Impossible à contourner sans exécuter un vrai navigateur : à consulter
# manuellement.
MANUAL_ONLY = [
    "CERT-FR (avis / alertes / bulletins)",
    "Recorded Future Blog",
    "Sekoia.io Blog",
    "CISA ICS Advisories",
    "Dragos Blog",
    "ENISA",
    "Legifrance",
    "Claroty Team82",
    "AttackerKB",
]
