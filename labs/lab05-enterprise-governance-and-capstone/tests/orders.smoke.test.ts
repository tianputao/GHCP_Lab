import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { createApp } from '../src/app.js';

describe('Lab 05 Capstone API — baseline smoke', () => {
  let server: Server;
  let baseUrl: string;

  before(async () => {
    const app = createApp();
    await new Promise<void>((resolve) => {
      server = app.listen(0, () => {
        const addr = server.address() as AddressInfo;
        baseUrl = `http://127.0.0.1:${addr.port}`;
        resolve();
      });
    });
  });

  after(async () => {
    await new Promise<void>((resolve, reject) => {
      server.close((err) => (err ? reject(err) : resolve()));
    });
  });

  it('GET /health and GET /orders respond with expected data', async () => {
    const health = await fetch(`${baseUrl}/health`);
    assert.equal(health.status, 200);

    const ordersRes = await fetch(`${baseUrl}/orders`);
    assert.equal(ordersRes.status, 200);
    const orders = (await ordersRes.json()) as Array<{ id: number; total: number }>;
    assert.equal(orders.length, 2);
    assert.equal(orders[0]?.total, 100);
    assert.equal(orders[1]?.total, 225);
  });
});
