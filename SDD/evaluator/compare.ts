import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createApp as createVibeApp } from '../track-a-vibe-coding/src/app.js';
import { createApp as createSddApp } from '../track-b-sdd/src/app.js';
import { runAcceptanceSuite } from './acceptance-suite.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SDD_ROOT = path.resolve(__dirname, '..');

function checkSpecTraceability(): { specReqs: string[]; missingInTests: string[] } {
  const refundSpec = readFileSync(
    path.join(SDD_ROOT, 'openspec/changes/add-partial-refund/specs/refunds/spec.md'),
    'utf8',
  );
  const orderSpec = readFileSync(
    path.join(SDD_ROOT, 'openspec/changes/add-partial-refund/specs/orders/spec.md'),
    'utf8',
  );
  const complianceTest = readFileSync(
    path.join(SDD_ROOT, 'track-b-sdd/tests/spec-compliance.test.ts'),
    'utf8',
  );

  const specReqs = [...new Set([...`${refundSpec}\n${orderSpec}`.matchAll(/\bREQ-\d{2}\b/g)].map((m) => m[0]))].sort();
  const missingInTests = specReqs.filter((req) => !complianceTest.includes(req));
  return { specReqs, missingInTests };
}

async function main(): Promise<void> {
  console.log('================================================================================');
  console.log('  SDD vs Vibe Coding — Automated Enterprise Acceptance Scorecard (12 Contracts)');
  console.log('================================================================================\n');

  const [vibeResults, sddResults] = await Promise.all([
    runAcceptanceSuite(createVibeApp),
    runAcceptanceSuite(createSddApp),
  ]);

  const vibePassed = vibeResults.filter((r) => r.passed).length;
  const sddPassed = sddResults.filter((r) => r.passed).length;

  console.log('| REQ    | Enterprise Requirement                                       | Vibe Coding | SDD (OpenSpec) |');
  console.log('|--------|--------------------------------------------------------------|-------------|----------------|');
  for (let i = 0; i < sddResults.length; i += 1) {
    const v = vibeResults[i]!;
    const s = sddResults[i]!;
    const title = s.title.slice(0, 60).padEnd(60, ' ');
    const vMark = v.passed ? ' PASS ✅    ' : ' FAIL ❌    ';
    const sMark = s.passed ? ' PASS ✅       ' : ' FAIL ❌       ';
    console.log(`| ${s.id} | ${title} |${vMark}|${sMark}|`);
  }

  console.log('\n--- Why Vibe Coding Failed (despite its own basic.test.ts passing!) ---');
  for (const r of vibeResults.filter((x) => !x.passed)) {
    console.log(`  ❌ [${r.id}] ${r.detail}`);
  }

  const traceability = checkSpecTraceability();
  console.log('\n--- OpenSpec Traceability Check ---');
  console.log(`  Requirements defined in OpenSpec delta: ${traceability.specReqs.length} (${traceability.specReqs.join(', ')})`);
  console.log(`  Missing in SDD compliance tests:        ${traceability.missingInTests.length}`);

  console.log('\n================================================================================');
  console.log(`  SCORE SUMMARY:  Track A (Vibe Coding) = ${vibePassed}/12   |   Track B (SDD) = ${sddPassed}/12`);
  console.log('================================================================================\n');

  if (sddPassed !== 12 || traceability.missingInTests.length > 0) {
    console.error('❌ SDD Track B must satisfy 12/12 acceptance criteria and 100% REQ traceability!');
    process.exit(1);
  }
  if (vibePassed >= 10) {
    console.error('❌ Vibe Coding baseline unexpectedly passed too many checks — verify demo contrast.');
    process.exit(1);
  }
}

await main();
