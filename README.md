# 🛡️ Cyber Watch — Sources de veille cybersécurité

![Mise à jour](https://img.shields.io/badge/Mise%20à%20jour-2026--07--04-blue)
![GRC](https://img.shields.io/badge/GRC-R%C3%A9glementaire-informational)
![Threat Intel](https://img.shields.io/badge/Threat-Intelligence-red)
![OT/ICS](https://img.shields.io/badge/OT%2FICS-SCADA-orange)
![CVE](https://img.shields.io/badge/CVE-Offensif-critical)
![License](https://img.shields.io/badge/License-MIT-green)

Agrégateur de sources tier 1 pour veille cyber professionnelle. Domaines couverts : GRC/Réglementaire, Threat Intelligence, OT/ICS/SCADA, CVE/Offensif.

## Sommaire

- [🏛️ GRC / Réglementaire](#️-grc--réglementaire-nis2--iso-27001--anssi)
- [🎯 Threat Intelligence](#-threat-intelligence-ioc--campagnes--apt)
- [⚙️ OT / ICS / SCADA](#️-ot--ics--scada-industriel--seveso--oiv)
- [💥 CVE / Offensif / Exploit](#-cve--offensif--exploit-oscp--red-team)
- [📋 Workflow recommandé](#-workflow-recommandé)
- [🎓 Veille vs montée en compétences](#-distinction-veille-vs-montée-en-compétences)
- [Licence](#licence)

---

## 🏛️ GRC / Réglementaire (NIS2 · ISO 27001 · ANSSI)

| Source | URL | RSS | Notes |
|---|---|---|---|
| ANSSI – Publications | https://cyber.gouv.fr/publications | Oui | Source primaire française, guides et recommandations officiels |
| CERT-FR – Bulletins | https://www.cert.ssi.gouv.fr/ | Oui | Avis CVE hebdomadaires, lecture obligatoire lundi matin |
| ENISA – Publications | https://www.enisa.europa.eu/publications | Oui | Équivalent européen ANSSI, threat landscape annuel, NIS2 |
| Legifrance – Cybersécurité | https://www.legifrance.gouv.fr/ | Oui | Transpositions réglementaires NIS2, CRA, veille légale OIV/OES |

---

## 🎯 Threat Intelligence (IOC · Campagnes · APT)

| Source | URL | RSS | Notes |
|---|---|---|---|
| Recorded Future Blog | https://www.recordedfuture.com/blog | Oui | Analyses APT, campagnes étatiques, attributions |
| Mandiant / Google TAG | https://cloud.google.com/blog/topics/threat-intelligence | Oui | Rapports d'attribution post-incident, cités par l'ANSSI |
| Bleeping Computer | https://www.bleepingcomputer.com/ | Oui | News opérationnelles, ransomware, incidents actifs, très réactif |
| The Hacker News | https://thehackernews.com/ | Oui | Agrégateur sérieux, bon ratio signal/bruit |
| Sekoia.io Blog | https://blog.sekoia.io/ | Oui | Threat intel française haut niveau, analyses MOA/IOC/TTPs |

---

## ⚙️ OT / ICS / SCADA (Industriel · SEVESO · OIV)

| Source | URL | RSS | Notes |
|---|---|---|---|
| CISA ICS-CERT Advisories | https://www.cisa.gov/ics-advisories | Oui | Référence mondiale vulnérabilités systèmes industriels |
| Dragos Blog | https://www.dragos.com/blog/ | Oui | Spécialiste OT/ICS, groupes ciblant infrastructures critiques |
| Claroty Research | https://claroty.com/team82/research | Oui | Vulnérabilités OT/IoT industriel, protocoles propriétaires |
| S4x Events Blog | https://s4xevents.com/blog/ | Oui | Conférence de référence ICS/SCADA, architecture et défense |

---

## 💥 CVE / Offensif / Exploit (OSCP · Red Team)

| Source | URL | RSS | Notes |
|---|---|---|---|
| NVD – NIST | https://nvd.nist.gov/ | Oui (API) | Base officielle CVE, filtrable par CVSS/produit/date |
| Exploit-DB | https://www.exploit-db.com/ | Oui | Base exploits publics Offensive Security, direct scope OSCP |
| Project Zero – Google | https://googleprojectzero.blogspot.com/ | Oui | 0-days, analyses de vulnérabilités profondes, très technique |
| Rapid7 / AttackerKB | https://attackerkb.com/ | Oui | Contextualisation CVE : exploitabilité réelle, priorisation |

---

## 📋 Workflow recommandé

- **Outil** : FreshRSS (self-hosted, gratuit) ou Feedly Free
- **Organisation** : 4 dossiers correspondant aux 4 catégories ci-dessus
- **Routine** : 15 minutes par jour, le matin
- **Objectif** : veille documentable et défendable (RNCP, entretien RSSI)

---

## 🎓 Distinction veille vs montée en compétences

| Activité | Type | Valorisation |
|---|---|---|
| Lecture CERT-FR / ANSSI | Veille | ✅ Veille professionnelle |
| Suivi Bleeping Computer | Veille | ✅ Veille opérationnelle |
| TryHackMe (top 9%) | Montée en compétences | ✅ Pratique offensive / OSCP prep |
| OSCP preparation | Montée en compétences | ✅ Certification offensive |

Ces deux activités sont complémentaires mais distinctes. Dans un dossier RNCP ou un entretien RSSI, les distinguer clairement est indispensable.

---

## 📧 Digest email automatique

Une GitHub Action (`.github/workflows/cyber-watch-digest.yml`) tourne chaque matin (6h UTC) et envoie un email HTML (dashboard par catégorie, avec repli texte brut) regroupant les nouveaux articles. Trois couches de collecte, combinées dans `cyber-watch/digest.py` :

1. **RSS/Atom** (`cyber-watch/feeds.py`) — ANSSI, Bleeping Computer, The Hacker News, S4x, Exploit-DB, Project Zero. Parsées en bibliothèque standard uniquement (pas de `feedparser` : sa dépendance `sgmllib3k` ne build plus avec les versions récentes de setuptools).
2. **API officielle** — NVD (CVE 2.0, gratuite, sans clé), qui remplace le flux RSS retiré par NIST.
3. **Scraping best-effort** (`cyber-watch/scraper.py`, navigateur headless Playwright) — CERT-FR (avis/alertes/bulletins), Recorded Future, Sekoia.io, Dragos, CISA ICS Advisories : sites sans flux exploitable ou protégés par un anti-bot léger. Le rendu navigateur passe certaines protections (Cloudflare "Bot Fight Mode") mais **pas de garantie** pour les protections plus dures type Akamai (fréquentes sur les sites `.gov`) — si une source scrapée remonte 0 résultat de façon persistante, les sélecteurs dans `scraper.py` sont probablement à ajuster. Comme ces pages n'ont pas de date de publication fiable, le dédoublonnage se fait via un état persistant (`cyber-watch/state.json`, committé par le workflow après chaque run) plutôt que par fenêtre de temps.

Sources sans flux, ni API, ni page à scraper de façon fiable — restent manuelles, listées en bas de chaque digest (`cyber-watch/feeds.py::MANUAL_ONLY`) :
- ENISA, Claroty Team82, Mandiant/Google Cloud : aucune source exploitable trouvée
- Legifrance ([API PISTE](https://piste.gouv.fr/registration)), AttackerKB (clé sur le profil) : API gratuite existante mais nécessitant un compte personnel, non configuré

### Configuration requise

Dans les paramètres du repo (`Settings` → `Secrets and variables` → `Actions`), ajouter 3 secrets :

| Secret | Valeur |
|---|---|
| `GMAIL_USER` | Adresse Gmail utilisée pour l'envoi |
| `GMAIL_APP_PASSWORD` | [Mot de passe d'application](https://myaccount.google.com/apppasswords) généré pour ce compte Gmail (pas le mot de passe du compte) |
| `DIGEST_TO` | Adresse de destination du digest |

Le workflow peut aussi être déclenché manuellement depuis l'onglet **Actions** (`workflow_dispatch`).

---

## Licence

MIT
