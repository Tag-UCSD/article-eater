# AI handoff prompt for governance-kit-v3

Paste this (and adapt details) when you ask an AI assistant to work inside a
project that has governance-kit-v3 installed.

---

You are helping with software development on a project that uses a small
governance layer called `governance-kit-v3`.

The project contains a `.governance` directory with:

- `SYSTEM_VISION.md` (why the system exists);
- `PROJECT_CONSTITUTION.md` (non-negotiable rules and invariants);
- `CONVERSATION_LEDGER.yml` (record of important human–AI coding sessions);
- `GOVERNANCE_CONFIG.yml` (paths and settings);
- optionally `release.keep.yml` and `deprecations.yml` (drift shield).

Before making major changes, you should skim the vision and constitution,
respect the documented constraints, and propose ledger entries at the end of
significant sessions.