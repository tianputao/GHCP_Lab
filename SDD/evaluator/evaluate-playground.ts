import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import type { Express } from 'express';
import { runAcceptanceSuite } from './acceptance-suite.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PLAYGROUND_APP = path.resolve(__dirname, '../playground/src/app.ts');

async function main(): Promise<void> {
  if (!existsSync(PLAYGROUND_APP)) {
    console.error('❌ playground/src/app.ts not found. Run `npm run reset:playground` first!');
    process.exit(1);
  }

  const mod = (await import(pathToFileURL(PLAYGROUND_APP).href)) as { createApp?: () => Express };
  if (typeof mod.createApp !== 'function') {
    console.error('❌ playground/src/app.ts must export `createApp()`.');
    process.exit(1);
  }

  const results = await runAcceptanceSuite(mod.createApp);
  const passed = results.filter((r) => r.passed).length;

  console.log('\n=== Student Playground · 12-Contract SDD Acceptance Evaluation ===\n');
  for (const r of results) {
    console.log(`${r.passed ? '✅' : '❌'} ${r.id} [${r.category}] ${r.title}`);
    if (!r.passed) {
      console.log(`     ↳ ${r.detail}`);
    }
  }
  console.log(`\nTotal Score: ${passed} / ${results.length}`);
  process.exit(passed === results.length ? 0 : 1);
}

await main();
