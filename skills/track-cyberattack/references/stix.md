# Reference H. The STIX 2.1 bundle and Navigator layer

Read this only if `tracker_tool.py stix` reports an error, or the user asks what the export holds.

`python3 work/scripts/tracker_tool.py stix tracker.json out/<attack>-stix.json` builds the bundle from the tracker and validates it. It also parses the bundle with the `stix2` Python library when that is installed.

## What a complete export preserves

A TIP that imports the bundle should get a usable copy of the attack tracker, not a handful of entities. So the bundle carries:

| Tracker section | STIX object |
|---|---|
| The attack as a whole | One `report` (types campaign and threat-report) whose `object_refs` list every other object. Its external references list every source. |
| The attack | One `campaign`, with aliases from the Name rows and first and last seen from the Attacker lane |
| A named actor (`summary.actor`) and each named attribution hypothesis | `intrusion-set` plus an `attributed-to` relationship. The relationship carries the ICD 203 likelihood and confidence in its description and a numeric `confidence` (likely 70, very likely 85, and so on). |
| Techniques | `attack-pattern` with the `mitre-attack` external ID and URL (kill chain `mitre-attack`, or `mitre-ics-attack` for ICS techniques), and a `uses` relationship that says how this attacker used it |
| CVEs in the `software` collection | `vulnerability` with affected and fixed versions, and a `targets` relationship |
| Victim sectors, and Confirmed victim organizations | `identity` (class or organization) with a `targets` relationship; the organization's description carries the data exposed |
| Every ledger claim | A `note` whose abstract starts with the claim ID, holding the paraphrase, status, credibility, sources, corroboration and basis. This is what makes each Cxx reference resolvable in another platform. |
| Timeline events, gaps, watch items, actions and source conflicts | A `note` each, with its ID in the abstract; a closed gap says which claim closed it |
| Handling mark | The official TLP 2.0 marking definition for `summary.tlp`, on every object |

Object IDs are deterministic (UUIDv5 from the attack name and each row's ID), so re-exporting after an update changes the same objects instead of creating duplicates. Attack patterns, CVEs and sector identities use IDs that are shared across attacks, so they merge across trackers in a TIP.

## What it leaves out on purpose

No `indicator` objects and no `indicates` relationships; network indicators are a separate job (offer ioc-extract-enrich if it is installed). No verbatim quotes. The kill chain and software rows for the SOC stay out of the bundle, apart from the CVEs. Private individuals are never named.

## Validation and import notes

`stix` checks the bundle itself (IDs, timestamps, references and markings) and parses it with the `stix2` library when that is installed. On the bundled test fixture (`tests/fixture`), the OASIS validator (`stix2-validator`) reported the bundle **valid** in its default mode. Its strict mode flags two recommendations, not requirements: object IDs are UUIDv5 rather than UUIDv4 (deliberate, so a re-export updates the same objects), and external references with URLs carry no hashes.

The bundle was built to import into MISP, OpenCTI and Cyware as a report with its contents, but it has not yet been test-imported into OpenCTI or MISP. If an import drops the notes, the claims are still listed in the report's description and in the Word report's ledger appendix. Say in the hand-over that the bundle has not been test-imported into the user's own platform.

## Navigator layer

`python3 work/scripts/tracker_tool.py navigator tracker.json out/<attack>-navigator.json` writes an ATT&CK Navigator layer for the Enterprise techniques (layer format 4.5, enterprise-attack, the version from `summary.attack_version`) and, when ICS techniques are mapped, a second layer `out/<attack>-navigator-ics.json` (ics-attack). Each technique is coloured and scored by occurrence (Observed 4, Reported 3, Capability 2, Assessed 1) and carries how it was used and its claims in the comment. The legend lists only the occurrences present. Open it at https://mitre-attack.github.io/attack-navigator/ with "Open Existing Layer".
