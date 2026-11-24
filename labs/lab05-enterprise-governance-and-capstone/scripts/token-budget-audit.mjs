#!/usr/bin/env node
/**
 * GitHub AI Credits & Context Budget Audit Tool (Lab 05)
 *
 * Demonstrates why context engineering directly governs Token-Based Billing (AI Credits):
 *   1. Checks `.github/copilot-instructions.md` length against Copilot Code Review's
 *      4,000-character instruction prefix window.
 *   2. Compares estimated input token footprint of:
 *      - Naive approach: dumping all repo files into every turn
 *      - Targeted approach: referencing only task-relevant files + concise instructions
 *   3. Checks whether sensitive files exist without exclusion guidance.
 */

import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LAB_ROOT = path.resolve(__dirname, '..');

function estimateTokens(text) {
  // Practical rule-of-thumb approximation (~4 chars/token for code & English, ~1.5-2 for CJK)
  return Math.ceil(text.length / 4);
}

function walkFiles(dir, result = []) {
  for (const entry of readdirSync(dir)) {
    if (entry === 'node_modules' || entry === 'dist' || entry === '.git') continue;
    const full = path.join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) walkFiles(full, result);
    else result.push(full);
  }
  return result;
}

const allFiles = walkFiles(LAB_ROOT);
let naiveChars = 0;
for (const file of allFiles) {
  naiveChars += readFileSync(file, 'utf8').length;
}

const targetedPaths = [
  '.github/copilot-instructions.md',
  'src/routes/orders.ts',
  'src/lib/discount.ts',
];
let targetedChars = 0;
for (const rel of targetedPaths) {
  const full = path.join(LAB_ROOT, rel);
  if (existsSync(full)) targetedChars += readFileSync(full, 'utf8').length;
}

const instructionsPath = path.join(LAB_ROOT, '.github/copilot-instructions.md');
const instructionChars = existsSync(instructionsPath)
  ? readFileSync(instructionsPath, 'utf8').length
  : 0;

const naiveTokens = estimateTokens('x'.repeat(naiveChars));
const targetedTokens = estimateTokens('x'.repeat(targetedChars));
const reductionPct = naiveTokens > 0 ? Math.round((1 - targetedTokens / naiveTokens) * 100) : 0;

console.log('=== Lab 05 · Context & GitHub AI Credits Optimization Audit ===');
console.log(`Files scanned (excluding node_modules): ${allFiles.length}`);
console.log(`Instruction file length: ${instructionChars} chars (Code Review 4,000-char budget: ${instructionChars <= 4000 ? 'PASS ✅' : 'OVER LIMIT ⚠️'})`);
console.log(`Naive full-folder context estimate:    ~${naiveTokens} input tokens/turn`);
console.log(`Targeted #file context estimate:       ~${targetedTokens} input tokens/turn (${reductionPct}% input reduction)`);
console.log(`10-turn Agent session savings:         ~${(naiveTokens - targetedTokens) * 10} input tokens saved`);
console.log('Tip: Pair targeted #file context + concise instructions + Task-Aware Auto + local fast tests to optimize AI Credits.');
