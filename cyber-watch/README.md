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

## Licence

MIT
