# Security policy

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a change of contact, of supported builds, or of the first real-data deployment.

## Reporting a vulnerability

Email **nakul.jain@aplyd.com** with the subject "Impact Platform security". Do not open a public GitHub issue for a vulnerability. Include the build (`VERSION.json`), what you did, what you saw and what you expected. Do not include real personal data, credentials or tokens; describe where they appear instead.

Response targets are not yet committed: TBD (owner: Nakul Jain). No acknowledgement time, fix time or bounty is promised by this file.

## Status of the product (read before relying on it)

- The Impact Platform is a development build. None of its 307 written requirements is accepted, it has had no penetration test, and it must not hold real personal data ([HANDOVER](docs/HANDOVER.md), [AGENTS.md](AGENTS.md) rule 11). Only synthetic data belongs on the staging server.
- Supported versions: the build on `main` (see `VERSION.json`). Older builds receive no separate fixes.
- Where to read the security design: [threat model](docs/current/Impact-Management-Security-Threat-Model-v1.1.md), [access-control specification](docs/current/Impact-Management-Access-Control-Specification-v1.1.md), [key and encryption register](docs/current/KEY-AND-ENCRYPTION-REGISTER.md), [governance map](docs/governance/README.md).

## Handling a suspected exposure

Operators follow [docs/governance/INCIDENT-PROCESS.md](docs/governance/INCIDENT-PROCESS.md) and the support runbook, section 4.11.
Never paste tokens, passwords, secrets or personal data into a report, ticket or chat.
