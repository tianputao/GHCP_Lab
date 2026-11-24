import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LAB_ROOT = path.resolve(__dirname, '..');

function extractText(result: Record<string, unknown>): string {
  const list = Array.isArray(result.content)
    ? (result.content as Array<{ type: string; text?: string }>)
    : [];
  return list.find((c) => c.type === 'text')?.text ?? '';
}

describe('Lab 03 — Custom Enterprise MCP Server (stdio E2E)', () => {
  let client: Client;
  let transport: StdioClientTransport;

  before(async () => {
    const tsxBin = path.join(LAB_ROOT, 'node_modules', '.bin', process.platform === 'win32' ? 'tsx.cmd' : 'tsx');
    transport = new StdioClientTransport({
      command: tsxBin,
      args: [path.join(LAB_ROOT, 'src', 'server.ts')],
      cwd: LAB_ROOT,
      stderr: 'pipe',
    });
    client = new Client({ name: 'lab03-test-client', version: '1.0.0' });
    await client.connect(transport);
  });

  after(async () => {
    await client.close();
  });

  it('lists all 3 enterprise tools', async () => {
    const response = await client.listTools();
    const names = response.tools.map((t) => t.name).sort();
    assert.deepEqual(names, ['check_deploy_policy', 'create_reorder_draft', 'query_inventory']);
  });

  it('query_inventory returns low-stock items accurately', async () => {
    const res = await client.callTool({
      name: 'query_inventory',
      arguments: { onlyLowStock: true },
    });
    const parsed = JSON.parse(extractText(res)) as { count: number; items: Array<{ sku: string }> };
    assert.equal(parsed.count, 2);
    const skus = parsed.items.map((i) => i.sku).sort();
    assert.deepEqual(skus, ['SKU-GPU-A100', 'SKU-SWITCH-400G']);
  });

  it('check_deploy_policy blocks production deploy during freeze window without override', async () => {
    const res = await client.callTool({
      name: 'check_deploy_policy',
      arguments: {
        service: 'payments-api',
        environment: 'production',
        humanApprovals: 1,
        securityScanPassed: false,
      },
    });
    const parsed = JSON.parse(extractText(res)) as { allowed: boolean; blockingReasons: string[] };
    assert.equal(parsed.allowed, false);
    assert.ok(parsed.blockingReasons.length >= 3);
  });

  it('create_reorder_draft validates SKU and computes director approval threshold', async () => {
    const res = await client.callTool({
      name: 'create_reorder_draft',
      arguments: { sku: 'SKU-GPU-A100', quantity: 5, requestedBy: 'alice@example.com' },
    });
    const parsed = JSON.parse(extractText(res)) as {
      estimatedTotalCents: number;
      requiresDirectorApproval: boolean;
      status: string;
    };
    assert.equal(parsed.estimatedTotalCents, 6_250_000);
    assert.equal(parsed.requiresDirectorApproval, true);
    assert.equal(parsed.status, 'DRAFT_PENDING_HUMAN_CONFIRMATION');
  });
});
