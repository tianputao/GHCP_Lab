#!/usr/bin/env node
/**
 * Cross-platform orchestrator for all sub-projects inside GHCP_Lab.
 * Usage:
 *   node scripts/run-all.mjs install
 *   node scripts/run-all.mjs test
 *   node scripts/run-all.mjs verify
 *   node scripts/run-all.mjs reset
 */

import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const PROJECTS = [
  { name: 'Lab 01 · Agent / Plan / Autopilot', dir: 'labs/lab01-agent-plan-and-autopilot' },
  { name: 'Lab 02 · Customization / Skills / Hooks', dir: 'labs/lab02-customization-skills-hooks' },
  { name: 'Lab 03 · Custom Enterprise MCP Server', dir: 'labs/lab03-mcp-server-and-tools' },
  { name: 'Lab 04 · Testing / Security / Review', dir: 'labs/lab04-testing-security-and-review' },
  { name: 'Lab 05 · Governance / AI Credits / Capstone', dir: 'labs/lab05-enterprise-governance-and-capstone' },
  { name: 'SDD    · Vibe Coding vs SDD (OpenSpec)', dir: 'SDD' },
];

const action = process.argv[2] ?? 'verify';
const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';

function runStep(label, cwd, args) {
  console.log(`\n============================================================`);
  console.log(`▶ ${label}`);
  console.log(`  cwd: ${path.relative(ROOT, cwd) || '.'}`);
  console.log(`  cmd: ${npmCmd} ${args.join(' ')}`);
  console.log(`============================================================`);
  const result = spawnSync(npmCmd, args, {
    cwd,
    stdio: 'inherit',
    env: process.env,
  });
  if (result.status !== 0) {
    console.error(`\n❌ Failed in "${label}" (exit code ${result.status ?? 'unknown'})`);
    process.exit(result.status ?? 1);
  }
}

for (const project of PROJECTS) {
  const cwd = path.join(ROOT, project.dir);
  if (!existsSync(path.join(cwd, 'package.json'))) {
    console.error(`❌ Missing package.json in ${project.dir}`);
    process.exit(1);
  }

  if (action === 'install') {
    runStep(`Install · ${project.name}`, cwd, ['install']);
  } else if (action === 'test') {
    runStep(`Test · ${project.name}`, cwd, ['test']);
  } else if (action === 'verify') {
    runStep(`Verify · ${project.name}`, cwd, ['run', 'verify']);
  } else if (action === 'reset') {
    if (project.dir === 'labs/lab02-customization-skills-hooks') {
      runStep(`Reset · ${project.name}`, cwd, ['run', 'reset']);
    } else if (project.dir === 'SDD') {
      runStep(`Reset · ${project.name}`, cwd, ['run', 'reset:playground']);
    }
  } else {
    console.error(`Unknown action: ${action}. Supported: install | test | verify | reset`);
    process.exit(1);
  }
}

console.log(`\n✅ All "${action}" checks completed cleanly across GHCP_Lab!`);
