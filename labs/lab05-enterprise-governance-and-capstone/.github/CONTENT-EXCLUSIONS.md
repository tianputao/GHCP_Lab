# Content Exclusions — Enterprise Setup Guide (2026)

> Configure exclusions in GitHub UI (**Business / Enterprise** plans):
> - Repo level: `Settings -> Copilot -> Content exclusion`
> - Org / Enterprise level: `AI Controls / Copilot -> Content exclusion`

## Recommended YAML Patterns

```yaml
"*":
  - "**/.env"
  - "**/.env.*"
  - "**/secrets/**"
  - "**/*.pem"
  - "**/*.key"
```

## Critical Governance Boundaries (2026)
1. **Not encryption & not `.gitignore`**: Content exclusion prevents supported Copilot surfaces from sending matched file contents to the model.
2. **Propagation time**: Changes can take up to **30 minutes** to propagate to open IDEs (reload window to refresh faster).
3. **Defense in depth**: Always combine Content Exclusions with **Deterministic Agent Hooks** (see Lab 02), repository access controls, secret scanning push protection, and never committing real production secrets.
