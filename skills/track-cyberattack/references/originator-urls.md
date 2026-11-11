# Reference F. Originator index pages

Read this at Step 3, when you fill the collection brief, and again for the originator round in Step 3.2. Search engines index agency and vendor pages poorly, so a direct fetch of the right index page usually finds the advisory in one call where two or three searches find nothing.

**How to use it.** For a government or vendor originator, fetch its index page from this table first, then open the matching entry. If the index page will not load or holds no matching entry, run one search restricted to the site (for example `site:cert.ssi.gouv.fr <victim or product>`). If both fail, register the originator as a Gap with `blocking` true, as Rubric B3.9 says.

These pages were checked on 9 November 2026. Rows marked "confirm on first use" were inferred from a related page; if one fails, fix the URL here so the next run benefits.

## Government and CERT

| Originator | Index page | Notes |
|---|---|---|
| CERT-FR (France) | https://www.cert.ssi.gouv.fr/alerte/ and https://www.cert.ssi.gouv.fr/avis/ | Alerts for active exploitation; avis for advisories. French. |
| CISA (US) | https://www.cisa.gov/news-events/cybersecurity-advisories | All advisory types, newest first. |
| CISA ICS advisories (US) | https://www.cisa.gov/news-events/ics-advisories | ICSA advisories for OT vendors. |
| CISA KEV (US) | https://www.cisa.gov/known-exploited-vulnerabilities-catalog | The date a CVE was added is an advisory event. |
| ENISA (EU) | https://www.enisa.europa.eu/news | |
| CCB (Belgium) | https://ccb.belgium.be/advisories | Also in /nl, /fr and /de. |
| CERT-SE (Sweden) | https://www.cert.se/ | Swedish news and advisories. |
| CERT-EE, RIA (Estonia) | https://ria.ee/en/news | Monthly "Situation in cyberspace" reports also sit here. |
| NCSC-NL (Netherlands) | https://advisories.ncsc.nl/ | Beveiligingsadviezen, Dutch. |
| BSI (Germany) | https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Cyber-Sicherheitslage/Technische-Sicherheitshinweise-und-Warnungen/Cyber-Sicherheitswarnungen/cyber-sicherheitswarnungen.html | Cyber security warnings. |
| ACN, CSIRT Italia (Italy) | https://www.csirt.gov.it/ | Confirm on first use; it may redirect to acn.gov.it. |
| CERT Polska (Poland) | https://cert.pl/en/news/ | |
| NCSC UK | https://www.ncsc.gov.uk/news | |

## OT and ICS vendors

A starter list of vendor advisory indexes. Add the vendors that matter to your sector.

| Vendor | Index page | Notes |
|---|---|---|
| Danfoss | https://www.danfoss.com/en/service-and-support/coordinated-vulnerability-disclosure/danfoss-security-advisories/ | DSA advisories. |
| Schneider Electric | https://www.se.com/ww/en/work/support/cybersecurity/security-notifications.jsp | SEVD notifications. |
| Siemens ProductCERT | https://cert-portal.siemens.com/productcert/ | SSA advisories. |
| Rockwell Automation | https://www.rockwellautomation.com/en-us/trust-center/security-advisories.html | |

To add an originator, append a row with the date you checked it. Keep the table to index pages that list advisories newest first; a single advisory URL belongs in the sources, not here.
