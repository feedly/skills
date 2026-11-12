# Reference I. The SOC hand-off (software and kill chain)

Read this at Step 10.

SOC and hunt teams triage many alerts a day. This section gives them the attack in a form they can act on, or paste into their own AI assistant: what software is involved, what happens at each stage, and which logs would show it. Build it from the ledger only.

## Software involved and versions (`software`)

One row per software item the chain uses, abuses or exploits on the victim side: the operating system, shells and terminals, signed binaries used for sideloading, built-in tools, runtimes the attacker brings in, directory services, browsers, and any exploited product.

- `version`: the exact version only when a source states it (for example "3.14.5"). If the activity is not tied to a version, write "Any". Never guess a version range. `check` warns when a version does not appear in the cited claims.
- If a CVE or other software vulnerability is involved, fill `cve`, `affected_versions`, `fixed_version` and `advisory_source` (the source ID of the vendor advisory) on that product's row.
- If no CVE or vulnerability is reported, add a ledger claim that says so (status Unknown or Reported, as the sources allow). The dashboard and report then state that there is no patch target.
- Leave out brands that are only impersonated (a fake update page using a browser's name), and say so in one line in that row's notes or in the summary.

## Kill chain for SOC (`killchain`)

One row per stage, in `order`, from initial access to post-compromise. Include stages that nobody observed, with `observed` "Not observed", so the reader can see what is missing.

| Field | What goes in it |
|---|---|
| `stage` | A plain name: Initial access, Execution, Persistence, Credential access, Lateral movement, Collection, Exfiltration, Impact |
| `tactic` | The current ATT&CK tactic shortname |
| `techniques` | Technique IDs, space separated |
| `process` | Image name and path; "N/A (no host stage)" for a stage with no host, such as an on-chain transfer or a change to a physical process |
| `action` | What happens, with the exact commands the sources give |
| `logs` | The log stream: network, firewall, proxy, DNS, endpoint telemetry, Windows Security or Sysmon event IDs, Defender, Defender for Identity, cloud audit logs. Say which streams must be turned on first, and any useful negative (a log the activity will not appear in). |
| `parent` | The parent process; "N/A (no host stage)" as for `process` |
| `artefacts` | Files, paths, hashes, registry values, task names |
| `network` | Domains, URLs and IPs, defanged (hxxp, [.]) |
| `detections` | Vendor signatures, alert names and hunting-query names from the sources |
| `hunt` | How to hunt for it |
| `sourced_fields` | The names of the fields above that come from the sources, space separated |
| `claim_ids` | The claims those fields rest on |

**Sourced versus analyst guidance.** Every process name, path, command and detection must trace to a ledger claim; add the claim first if it is missing. List each sourced field in `sourced_fields`. Any other filled field (parent processes, log streams, hunt logic, time windows) must start with "Analyst guidance:", or be "Not available in provided reports". A stage with no host says "N/A (no host stage)" for `process` and `parent`, rather than "Not available", so the reader knows nothing is missing. `check` enforces this, along with defanging and claim IDs for every observed or reported stage.

**Cases with no host or no technical reporting.** For an attack on industrial control systems, use ATT&CK for ICS tactic shortnames in `tactic` (for example impair-process-control). For a crypto theft, the on-chain stages have no host; describe the transaction in `action` and name the chain explorer or exchange records in `logs` as analyst guidance. For an actor or law enforcement case with no technical reporting, leave both collections empty and write one line in `summary.soc_note` saying why; the dashboard and report show that line instead of a table of "Not available".

## Example rows

```json
{"software": [
  {"software_id": "P01", "software": "FerryGate file-transfer appliance", "version": "9.4.1", "role": "Exploited service",
   "how": "Vulnerable to CVE-2026-41234", "cve": "CVE-2026-41234", "affected_versions": "9.0 to 9.4.1",
   "fixed_version": "9.4.2", "advisory_source": "S02", "claim_ids": "C04"},
  {"software_id": "P02", "software": "IIS worker process (w3wp.exe)", "version": "Any", "role": "Abused built-in process",
   "how": "Spawned cmd.exe", "claim_ids": "C06"}],
 "killchain": [
  {"stage_id": "Q02", "order": 2, "stage": "Execution and persistence", "observed": "Reported", "tactic": "persistence",
   "techniques": "T1059.003 T1505.003", "process": "w3wp.exe spawns cmd.exe", "parent": "w3wp.exe",
   "artefacts": "health.aspx in the web root",
   "logs": "Analyst guidance: Sysmon Event ID 1 and 11, or EDR process and file telemetry; needs process creation logging turned on",
   "hunt": "Analyst guidance: w3wp.exe with a cmd.exe or powershell.exe child",
   "sourced_fields": "process artefacts parent", "claim_ids": "C06"},
  {"stage_id": "Q03", "order": 3, "stage": "Exfiltration", "observed": "Not observed", "tactic": "exfiltration",
   "action": "Not available in provided reports"}]}
```

Both collections appear on the dashboard's "Kill chain (SOC)" tab and in the Word report's "Kill chain for SOC hand-off" chapter. They stay out of the STIX bundle, apart from CVEs. The audit at Step 12 checks these rows too (QA7).
