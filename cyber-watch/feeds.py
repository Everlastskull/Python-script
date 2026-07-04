"""Liste des flux RSS de veille, groupés par catégorie (cf. README.md)."""

FEEDS = {
    "GRC / Réglementaire": [
        ("ANSSI – Actualités", "https://cyber.gouv.fr/actualites/rss/"),
        ("CERT-FR – Avis", "https://www.cert.ssi.gouv.fr/avis/rss/"),
        ("CERT-FR – Alertes", "https://www.cert.ssi.gouv.fr/alerte/rss/"),
        ("CERT-FR – Bulletins d'actualité", "https://www.cert.ssi.gouv.fr/actualite/rss/"),
    ],
    "Threat Intelligence": [
        ("Recorded Future Blog", "https://www.recordedfuture.com/category/cyber/feed/"),
        ("Bleeping Computer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("Sekoia.io Blog", "https://blog.sekoia.io/feed/"),
    ],
    "OT / ICS / SCADA": [
        ("CISA ICS Advisories", "https://us-cert.cisa.gov/ics/advisories/advisories.xml"),
        ("Dragos Blog", "https://www.dragos.com/blog/feed/"),
        ("S4x Events Blog", "https://s4xevents.com/feed/"),
    ],
    "CVE / Offensif": [
        ("Exploit-DB", "https://www.exploit-db.com/rss.xml"),
        ("Project Zero – Google", "https://googleprojectzero.blogspot.com/feeds/posts/default"),
    ],
}
