# Feedly Skills and Prompts

Community cyber threat intelligence (CTI) resources for Claude, maintained by
[Feedly](https://feedly.com), in two forms: a [Claude Code plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugins) 
of installable skills for use inside Claude, and a library of standalone prompts you can copy and paste anywhere.

This repo is both the marketplace and the single plugin it distributes,
`feedly-cti-skills`, bundling skills for threat intel triage, IOC
enrichment, MITRE ATT&CK mapping, phishing analysis, report writing, and
dark web monitoring workflows.

## Install

### Claude Code

```
/plugin marketplace add feedly/skills
/plugin install feedly-cti-skills@feedly-skills
```

Then reload plugins (`/reload-plugins` or restart Claude Code) to pick up the skills.

### claude.ai / Claude Cowork / Claude Desktop

1. Go to **Customize → Plugins → Add marketplace**.
2. Paste the GitHub URL for this repo (`https://github.com/feedly/skills`)
3. Install `feedly-cti-skills` from the marketplace listing.

Alternatively, visit [Releases](https://github.com/feedly/skills/releases) to
download each skill as a standalone, bundled `.skill` file — useful if you'd
rather install a single skill by hand than add the whole marketplace.

## What's included

Skills live under [`skills/`](skills/), one folder per skill, each containing a `SKILL.md`.

| Skill | Description |
| --- | --- |
| [`intelligence-requirements-builder`](skills/intelligence-requirements-builder/) | Turns a vague stakeholder ask into a structured set of intelligence requirements (EEIs, collection guidance, success criteria, deliverables, criticality rating), output as markdown, Word, and CSV. |
| [`cti-risk-delta`](skills/cti-risk-delta/) | Rates a threat with OWASP before and after CTI action, with a financial exposure band sized to the organization. Output as markdown and Word. |
| [`create-sigma-rule`](skills/create-sigma-rule/) | Turns a threat report, advisory, malware write-up, or log sample into draft Sigma detection rules, checked with sigma-cli when a shell is available, plus a validation note. |

### Prompts

Standalone prompts (not packaged as Claude Code skills) are hosted under [`prompts/`](prompts/).

#### Feedly's Complete CTI Prompt Library

[`prompts/feedly-complete-cti-prompt-library/`](prompts/feedly-complete-cti-prompt-library/) hosts *Feedly's Complete CTI Prompt Library* —
44 prompts from four Feedly TI Essentials posts, mirrored here verbatim (unmodified,
as published) for easy access and version control. These are plain prompts, not
Claude Code skills — copy/paste them as needed. See
[`prompts/feedly-complete-cti-prompt-library/README.md`](prompts/feedly-complete-cti-prompt-library/README.md) for the full index and usage terms.

## Versioning

`plugin.json` currently omits a `version` field — every commit to `main` is
treated as the latest version. This is the simplest setup for an
actively-updated skill set. We may switch to explicit semver + release
channels later if update noise becomes a problem for users.

## Contributing

Because this repo is public, every skill must be reviewed to strip any
Feedly-internal specifics (customer names, internal URLs, credentials,
proprietary detection logic) before being added. Skills should describe
general CTI workflows, not Feedly-internal ones.

Before opening a PR, run from the repo root:

```
claude plugin validate .
```

## License

MIT — see [LICENSE](LICENSE).
