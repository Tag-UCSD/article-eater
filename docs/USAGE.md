# Usage overview

After installing governance-kit-v3 into a project, you will see a
`.governance` directory with:

- `SYSTEM_VISION.md`
- `PROJECT_CONSTITUTION.md`
- `CONVERSATION_LEDGER.yml`
- `GOVERNANCE_CONFIG.yml`
- `release.keep.yml` and `deprecations.yml` if drift shield is enabled.

The guard script rendered from `conversation_guard.py.tpl` can be run as
`.governance/conversation_guard.py` to perform basic checks on these files.