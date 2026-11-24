import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HOOK_SCRIPT = path.resolve(__dirname, '../prep/hooks/guard-tools.mjs');

function runHook(event) {
  const res = spawnSync(process.execPath, [HOOK_SCRIPT], {
    input: JSON.stringify(event),
    encoding: 'utf8',
  });
  assert.equal(res.status, 0, `Hook process failed: ${res.stderr}`);
  return JSON.parse(res.stdout.trim());
}

describe('Lab 02 — Deterministic preToolUse Hook Guardrails', () => {
  it('blocks destructive rm -rf shell command', () => {
    const decision = runHook({
      toolName: 'bash',
      toolArgs: { command: 'rm -rf /tmp/project' },
    });
    assert.equal(decision.permissionDecision, 'deny');
    assert.match(decision.permissionDecisionReason, /destructive-rm/);
  });

  it('blocks git push --force', () => {
    const decision = runHook({
      toolName: 'run_in_terminal',
      toolArgs: { command: 'git push origin main --force' },
    });
    assert.equal(decision.permissionDecision, 'deny');
    assert.match(decision.permissionDecisionReason, /force-push/);
  });

  it('blocks reading sensitive .env and secrets files', () => {
    const envDecision = runHook({
      toolName: 'read_file',
      toolArgs: { filePath: '/workspace/.env.production' },
    });
    assert.equal(envDecision.permissionDecision, 'deny');

    const secretDecision = runHook({
      toolName: 'view',
      toolArgs: { path: 'secrets/api-keys.txt' },
    });
    assert.equal(secretDecision.permissionDecision, 'deny');
  });

  it('allows normal safe development commands and source file reads', () => {
    const cmdDecision = runHook({
      toolName: 'bash',
      toolArgs: { command: 'npm run typecheck && npm test' },
    });
    assert.equal(cmdDecision.permissionDecision, 'allow');

    const fileDecision = runHook({
      toolName: 'read_file',
      toolArgs: { filePath: 'src/repositories/task-repository.ts' },
    });
    assert.equal(fileDecision.permissionDecision, 'allow');
  });
});
