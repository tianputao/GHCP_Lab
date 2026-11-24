#!/usr/bin/env node
/**
 * Deterministic Copilot `preToolUse` Hook Guardrail (2026 Copilot Harness).
 *
 * Unlike prose instructions (which are probabilistic guidance for an LLM),
 * hooks run deterministically before every tool call and can enforce hard
 * security boundaries.
 *
 * Reads a JSON hook event from stdin and writes a JSON decision to stdout:
 *   { "permissionDecision": "allow" | "deny", "permissionDecisionReason": "..." }
 */

import { appendFileSync, readFileSync } from 'node:fs';
import path from 'node:path';

const DANGEROUS_SHELL_PATTERNS = [
  { name: 'destructive-rm', regex: /\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b|\brm\s+-rf\b/ },
  { name: 'force-push', regex: /\bgit\s+push\b[^\n]*(--force|-f)\b/ },
  { name: 'pipe-to-shell', regex: /\b(curl|wget)\b[^\n]*\|\s*(ba)?sh\b/ },
  { name: 'privilege-escalation', regex: /\bsudo\b/ },
];

const SENSITIVE_FILE_PATTERNS = [
  /(^|[\\/])\.env(\.|$)/i,
  /(^|[\\/])secrets[\\/]/i,
  /\.(pem|key)$/i,
];

export function evaluateToolEvent(event) {
  const toolName = String(event?.toolName ?? event?.tool_name ?? '').toLowerCase();
  const rawArgs = event?.toolArgs ?? event?.tool_input ?? event?.input ?? {};
  const argsText = typeof rawArgs === 'string' ? rawArgs : JSON.stringify(rawArgs);

  // 1. Block destructive shell commands regardless of prompt wording
  if (/(shell|bash|terminal|powershell|run_in_terminal|command)/.test(toolName)) {
    for (const rule of DANGEROUS_SHELL_PATTERNS) {
      if (rule.regex.test(argsText)) {
        return {
          permissionDecision: 'deny',
          permissionDecisionReason: `Blocked by deterministic hook [${rule.name}]: destructive or privileged shell command is not permitted in this lab.`,
        };
      }
    }
  }

  // 2. Block reading/writing sensitive secret paths
  if (/(read|view|edit|write|create|patch|file|shell|bash|terminal)/.test(toolName)) {
    const candidateStrings = [];
    if (typeof rawArgs === 'string') {
      candidateStrings.push(rawArgs);
    } else if (rawArgs && typeof rawArgs === 'object') {
      for (const value of Object.values(rawArgs)) {
        if (typeof value === 'string') candidateStrings.push(value);
      }
    }
    for (const value of candidateStrings) {
      for (const pattern of SENSITIVE_FILE_PATTERNS) {
        if (pattern.test(value)) {
          return {
            permissionDecision: 'deny',
            permissionDecisionReason: `Blocked by deterministic hook [sensitive-path]: access to "${value}" is restricted.`,
          };
        }
      }
    }
  }

  return {
    permissionDecision: 'allow',
    permissionDecisionReason: 'Allowed by lab guardrail policy.',
  };
}

// Execute as CLI hook when invoked directly
const isMain = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname);
if (isMain) {
  const raw = readFileSync(0, 'utf8').trim();
  const event = raw ? JSON.parse(raw) : {};
  const decision = evaluateToolEvent(event);

  if (process.env.HOOK_AUDIT_LOG) {
    const entry = JSON.stringify({
      timestamp: new Date().toISOString(),
      toolName: event?.toolName ?? event?.tool_name ?? 'unknown',
      decision: decision.permissionDecision,
      reason: decision.permissionDecisionReason,
    });
    appendFileSync(process.env.HOOK_AUDIT_LOG, `${entry}\n`, 'utf8');
  }

  process.stdout.write(`${JSON.stringify(decision)}\n`);
}
