#!/usr/bin/env node
/**
 * Bundled deterministic verification script for the `scaffold-feature` Agent Skill.
 * Checks target directories for common standards violations:
 *   - explicit `any` annotations
 *   - `var ` declarations
 *   - dynamic `eval(` calls
 *   - raw string concatenation inside SQL statements
 */

import { readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';

const targets = process.argv.slice(2);
if (targets.length === 0) {
  console.error('Usage: node check-conventions.mjs <dir1> [dir2...]');
  process.exit(2);
}

const RULES = [
  { id: 'NO_ANY', regex: /:\s*any\b|\bas\s+any\b/, message: 'Avoid explicit `any` type' },
  { id: 'NO_VAR', regex: /\bvar\s+\w+/, message: 'Use `const` or `let` instead of `var`' },
  { id: 'NO_EVAL', regex: /\beval\s*\(/, message: 'Do not use dynamic `eval()`' },
  {
    id: 'NO_SQL_CONCAT',
    regex: /(["'`])(?:SELECT|INSERT|UPDATE|DELETE)\b[^"'`]*(\$\{|\+\s*\w)/i,
    message: 'Possible unparameterized SQL string concatenation',
  },
];

function walkTs(dirPath, collected = []) {
  for (const entry of readdirSync(dirPath)) {
    const full = path.join(dirPath, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) {
      walkTs(full, collected);
    } else if (full.endsWith('.ts')) {
      collected.push(full);
    }
  }
  return collected;
}

const violations = [];
let filesScanned = 0;

for (const target of targets) {
  const abs = path.resolve(process.cwd(), target);
  const files = statSync(abs).isDirectory() ? walkTs(abs) : [abs];
  for (const file of files) {
    filesScanned += 1;
    const lines = readFileSync(file, 'utf8').split(/\r?\n/);
    lines.forEach((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('//') || trimmed.startsWith('*')) return;
      for (const rule of RULES) {
        if (rule.regex.test(line)) {
          violations.push({
            file: path.relative(process.cwd(), file),
            line: idx + 1,
            rule: rule.id,
            message: rule.message,
          });
        }
      }
    });
  }
}

if (violations.length > 0) {
  console.error(`❌ Convention check failed (${violations.length} issue(s) across ${filesScanned} files):`);
  for (const v of violations) {
    console.error(`  - ${v.file}:${v.line} [${v.rule}] ${v.message}`);
  }
  process.exit(1);
}

console.log(`✅ Convention check passed (${filesScanned} TypeScript files scanned, 0 violations).`);
