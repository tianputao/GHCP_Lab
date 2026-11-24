#!/usr/bin/env node
/**
 * Copies `SDD/base-app/` cleanly into `SDD/playground/` so students or instructors
 * can repeatedly practice Vibe Coding vs SDD from an identical brownfield starting point.
 */

import { cpSync, existsSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SDD_ROOT = path.resolve(__dirname, '..');
const SOURCE = path.join(SDD_ROOT, 'base-app');
const TARGET = path.join(SDD_ROOT, 'playground');

if (existsSync(TARGET)) {
  rmSync(TARGET, { recursive: true, force: true });
}
cpSync(SOURCE, TARGET, { recursive: true });
console.log('✅ Reset SDD/playground/ from clean brownfield SDD/base-app/.');
console.log('   Next: run Vibe Coding or SDD inside SDD/playground/, then evaluate with `npm run evaluate:playground`.');
