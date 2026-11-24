#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Resetting Lab 02 to clean BEFORE state..."
rm -rf .github api/test-route.ts dist .hook-audit.log
echo "✅ Lab 02 reset complete. Run 'npm run verify:env' to confirm clean state."
