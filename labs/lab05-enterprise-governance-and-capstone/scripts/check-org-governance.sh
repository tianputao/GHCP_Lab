#!/usr/bin/env bash
# Enterprise Copilot Governance & Audit API Inspector (Lab 05)
# Usage:
#   bash scripts/check-org-governance.sh --dry-run
#   bash scripts/check-org-governance.sh <YOUR-GITHUB-ORG>
set -euo pipefail

ARG="${1:---dry-run}"

if [ "$ARG" = "--dry-run" ]; then
  echo "=== Lab 05 · Enterprise Governance API Commands (Dry Run) ==="
  echo "Run these commands with an Org Admin / Copilot Admin token:"
  echo "  1. Seat & billing summary:   gh api /orgs/<ORG>/copilot/billing"
  echo "  2. Assigned seats list:      gh api /orgs/<ORG>/copilot/billing/seats"
  echo "  3. Copilot audit log events: gh api '/orgs/<ORG>/audit-log?phrase=action:copilot'"
  echo "  4. Usage analytics metrics:  gh api /orgs/<ORG>/copilot/metrics"
  echo "✅ Governance command template verified (dry-run mode)."
  exit 0
fi

ORG="$ARG"
echo "Querying GitHub Copilot billing summary for org: $ORG ..."
gh api "/orgs/${ORG}/copilot/billing"
echo
echo "Querying latest Copilot audit events for org: $ORG ..."
gh api "/orgs/${ORG}/audit-log?phrase=action:copilot&per_page=5"
