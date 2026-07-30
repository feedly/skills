# feedly-skills

A [Claude Code plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugins) of
community cyber threat intelligence (CTI) skills, maintained by [Feedly](https://feedly.com).

This repo hosts both the marketplace and the single plugin it distributes:
`feedly-cti-skills` — a bundle of skills covering threat intel triage, IOC
enrichment, MITRE ATT&CK mapping, phishing analysis, report writing, and
dark web monitoring workflows.

All skills ship as one plugin so there's a single install command. We may
split into themed plugins later if usage patterns call for it.

## Install

### Claude Code

```
/plugin marketplace add feedly/skills
/plugin install feedly-cti-skills@feedly-skills
```

Then reload plugins (`/reload-plugins` or restart Claude Code) to pick up the skills.

### claude.ai / Claude Cowork / Claude Desktop

1. Go to **Customize → Plugins → Add marketplace**.
2. Paste the GitHub URL for this repo (`https://github.com/feedly/skills`), or upload a
   packaged plugin file directly.
3. Install `feedly-cti-skills` from the marketplace listing.

## What's included

Skills live under [`plugins/feedly-cti-skills/skills/`](plugins/feedly-cti-skills/skills/).
See that directory's README for the skill format and contribution guidelines.

| Skill | Description |
| --- | --- |
| _(none yet — skeleton repo, skills to be added)_ | |

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
