# 🛡️ Veille Cyber Quotidienne

![Mise à jour](https://img.shields.io/badge/Mise%20à%20jour-2026--07--04-blue)
![Automatisé](https://img.shields.io/badge/Envoi-quotidien%206h%20UTC-success)
![GRC](https://img.shields.io/badge/GRC-R%C3%A9glementaire-informational)
![Threat Intel](https://img.shields.io/badge/Threat-Intelligence-red)
![OT/ICS](https://img.shields.io/badge/OT%2FICS-SCADA-orange)
![CVE](https://img.shields.io/badge/CVE-Offensif-critical)
![License](https://img.shields.io/badge/License-MIT-green)

Système de veille cybersécurité automatisé, par **Matthieu Maurial**. Chaque matin, une GitHub Action agrège une sélection de sources tier 1 et envoie un **email HTML** (dashboard par catégorie) regroupant les nouveaux articles des dernières 24 h — sans intervention manuelle.

Domaines couverts : GRC/Réglementaire · Threat Intelligence · OT/ICS/SCADA · CVE/Offensif.

## Sommaire

- [⚙️ Comment ça marche](#️-comment-ça-marche)
- [📥 Sources collectées](#-sources-collectées)
  - [🏛️ GRC / Réglementaire](#️-grc--réglementaire)
  - [🎯 Threat Intelligence](#-threat-intelligence)
  - [⚙️ OT / ICS / SCADA](#️-ot--ics--scada)
  - [💥 CVE / Offensif](#-cve--offensif)
- [📝 Sources en consultation manuelle](#-sources-en-consultation-manuelle)
- [🔧 Installation & configuration](#-installation--configuration)
- [📂 Structure du dépôt](#-structure-du-dépôt)
- [🎓 Veille vs montée en compétences](#-veille-vs-montée-en-compétences)
- [Licence](#licence)

---

## ⚙️ Comment ça marche

Une GitHub Action (`.github/workflows/cyber-watch-digest.yml`) s'exécute chaque jour à **6 h UTC** (déclenchement manuel également possible). Elle lance `cyber-watch/digest.py`, qui collecte les articles via **trois couches complémentaires**, construit un email HTML + repli texte, et l'envoie par SMTP Gmail.

| Couche | Mécanisme | Sources |
|---|---|---|
| **RSS / Atom** | Parsing en bibliothèque standard¹ | ANSSI, Bleeping Computer, The Hacker News, S4x, Exploit-DB, Project Zero |
| **API officielle** | Requête JSON directe | NVD (API CVE 2.0, gratuite, sans clé — remplace le flux RSS retiré par NIST) |
| **Scraping best-effort** | Navigateur headless Playwright² | CERT-FR (avis/alertes/bulletins), Recorded Future, Sekoia.io, Dragos, CISA ICS Advisories |

¹ Pas de `feedparser` : sa dépendance `sgmllib3k` ne se compile plus avec les versions récentes de setuptools. Le RSS/Atom est parsé avec `xml.etree`.

² Le rendu navigateur passe certaines protections anti-bot légères (Cloudflare « Bot Fight Mode »), mais **sans garantie** pour les protections plus dures (type Akamai, fréquentes sur les sites `.gov`). Si une source scrapée remonte 0 résultat de façon persistante, c'est généralement que le site a changé sa structure HTML : les sélecteurs dans `scraper.py` sont alors à ajuster.

**Dédoublonnage.** Les pages scrapées n'ayant pas de date de publication fiable, le suivi des articles déjà envoyés se fait via un état persistant (`cyber-watch/state.json`), committé par le workflow après chaque run. Seuls les articles **nouveaux** remontent d'un jour à l'autre. Les sources RSS/API, elles, utilisent une fenêtre glissante de 24 h.

---

## 📥 Sources collectées

Colonne **Collecte** : `RSS` / `API` = automatisé structuré · `Scraping` = automatisé best-effort · `Manuel` = non automatisable (voir plus bas).

### 🏛️ GRC / Réglementaire

*NIS2 · ISO 27001 · ANSSI*

| Source | Collecte | Notes |
|---|---|---|
| [ANSSI – Actualités](https://cyber.gouv.fr/actualites/) | RSS | Source primaire française, guides et recommandations officiels |
| [CERT-FR – Avis / Alertes / Bulletins](https://www.cert.ssi.gouv.fr/) | Scraping | Avis CVE, alertes d'exploitation active, synthèse hebdo |
| [ENISA – Publications](https://www.enisa.europa.eu/publications) | Manuel | Équivalent européen ANSSI, threat landscape annuel, NIS2 |
| [Legifrance – Cybersécurité](https://www.legifrance.gouv.fr/) | Manuel | Transpositions réglementaires NIS2, CRA, veille légale OIV/OES |

### 🎯 Threat Intelligence

*IOC · Campagnes · APT*

| Source | Collecte | Notes |
|---|---|---|
| [Bleeping Computer](https://www.bleepingcomputer.com/) | RSS | News opérationnelles, ransomware, incidents actifs, très réactif |
| [The Hacker News](https://thehackernews.com/) | RSS | Agrégateur sérieux, bon ratio signal/bruit |
| [Recorded Future Blog](https://www.recordedfuture.com/blog) | Scraping | Analyses APT, campagnes étatiques, attributions |
| [Sekoia.io Blog](https://blog.sekoia.io/) | Scraping | Threat intel française haut niveau, analyses MOA/IOC/TTPs |
| [Mandiant / Google TAG](https://cloud.google.com/blog/topics/threat-intelligence) | Manuel | Rapports d'attribution post-incident, cités par l'ANSSI |

### ⚙️ OT / ICS / SCADA

*Industriel · SEVESO · OIV*

| Source | Collecte | Notes |
|---|---|---|
| [CISA ICS Advisories](https://www.cisa.gov/news-events/ics-advisories) | Scraping | Référence mondiale vulnérabilités systèmes industriels |
| [Dragos Blog](https://www.dragos.com/blog/) | Scraping | Spécialiste OT/ICS, groupes ciblant infrastructures critiques |
| [S4x Events Blog](https://s4xevents.com/) | RSS | Conférence de référence ICS/SCADA, architecture et défense |
| [Claroty Team82](https://claroty.com/team82/research) | Manuel | Vulnérabilités OT/IoT industriel, protocoles propriétaires |

### 💥 CVE / Offensif

*OSCP · Red Team*

| Source | Collecte | Notes |
|---|---|---|
| [NVD – NIST](https://nvd.nist.gov/) | API | Base officielle CVE, filtrable par CVSS/produit/date |
| [Exploit-DB](https://www.exploit-db.com/) | RSS | Base exploits publics Offensive Security, direct scope OSCP |
| [Project Zero – Google](https://googleprojectzero.blogspot.com/) | RSS | 0-days, analyses de vulnérabilités profondes, très technique |
| [Rapid7 / AttackerKB](https://attackerkb.com/) | Manuel | Contextualisation CVE : exploitabilité réelle, priorisation |

---

## 📝 Sources en consultation manuelle

Ces sources sont listées en bas de chaque digest (`cyber-watch/feeds.py::MANUAL_ONLY`) mais restent à consulter à la main :

- **Aucune source exploitable trouvée** (ni flux, ni API, ni page scrapable de façon fiable) : ENISA, Claroty Team82, Mandiant / Google Cloud.
- **API gratuite existante mais nécessitant un compte personnel** (non configuré) : Legifrance ([API via PISTE](https://piste.gouv.fr/registration)), AttackerKB (clé générée sur le profil utilisateur). Pour les activer : créer le compte, récupérer la clé, l'ajouter en secret GitHub, puis brancher l'API dans `digest.py`.

---

## 🔧 Installation & configuration

Le workflow tourne clé en main une fois **3 secrets** ajoutés dans le dépôt (`Settings` → `Secrets and variables` → `Actions` → *New repository secret*) :

| Secret | Valeur |
|---|---|
| `GMAIL_USER` | Adresse Gmail utilisée pour l'envoi |
| `GMAIL_APP_PASSWORD` | [Mot de passe d'application](https://myaccount.google.com/apppasswords) généré pour ce compte Gmail — **pas** le mot de passe du compte (nécessite la validation en 2 étapes activée) |
| `DIGEST_TO` | Adresse de destination du digest |

**Déclenchement manuel** (pour tester sans attendre 6 h) : onglet **Actions** → *Cyber Watch — Digest email* → *Run workflow*.

**Personnalisation** :
- Fenêtre de veille : variable d'env. `DIGEST_LOOKBACK_HOURS` (défaut 24).
- Heure d'envoi : champ `cron` dans le workflow.
- Ajouter/retirer une source RSS : `cyber-watch/feeds.py`. Une source scrapée : `cyber-watch/scraper.py`.

Aucune dépendance à installer pour les couches RSS/API (bibliothèque standard). Le scraping installe Playwright + Chromium à la volée dans le job CI.

---

## 📂 Structure du dépôt

```
.github/workflows/cyber-watch-digest.yml   Workflow planifié (cron + manuel)
cyber-watch/
├── digest.py    Orchestration : collecte, rendu HTML/texte, envoi email
├── feeds.py     Sources RSS + liste MANUAL_ONLY
├── scraper.py   Scraping navigateur headless (sources sans flux)
├── state.py     Chargement/sauvegarde de l'état de dédoublonnage
└── state.json   Articles déjà envoyés (mis à jour par le workflow)
```

---

## 🎓 Veille vs montée en compétences

| Activité | Type | Valorisation |
|---|---|---|
| Lecture CERT-FR / ANSSI | Veille | ✅ Veille professionnelle |
| Suivi Bleeping Computer | Veille | ✅ Veille opérationnelle |
| TryHackMe (top 9 %) | Montée en compétences | ✅ Pratique offensive / OSCP prep |
| Préparation OSCP | Montée en compétences | ✅ Certification offensive |

Ces deux activités sont complémentaires mais **distinctes**. Dans un dossier RNCP ou un entretien RSSI, les distinguer clairement est indispensable : la veille documente une posture professionnelle continue ; la montée en compétences atteste d'une pratique technique. Ce dépôt sert la première, de façon automatisée et donc défendable (traçabilité des sources, régularité prouvée par l'historique des runs).

---

## Licence

MIT
