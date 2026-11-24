import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { createApp } from '../src/app.js';

/**
 * Classic Vibe Coding illusion:
 * Only tests the basic happy path -> ALL GREEN!
 * Gives false confidence while 8+ production financial defects remain hidden.
 */
describe('Track A (Vibe Coding) — Own Happy-Path Test (False Sense of Security)', () => {
  let server: Server;
  let baseUrl: string;

  before(async () => {
    await new Promise<void>((resolve) => {
      server = createApp().listen(0, () => {
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

  it('refunds 3000 cents from a 10000 cent paid order', async () => {
    const createRes = await fetch(`${baseUrl}/orders`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ customerId: 'cust-vibe', grossAmountCents: 10000 }),
    });
    const order = (await createRes.json()) as { id: string };
    await fetch(`${baseUrl}/orders/${order.id}/pay`, { method: 'POST' });

    const refundRes = await fetch(`${baseUrl}/orders/${order.id}/refunds`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ amountCents: 3000 }),
    });
    assert.equal(refundRes.status, 201);
    const body = (await refundRes.json()) as {
      order: { status: string; refundedAmountCents: number };
    };
    assert.equal(body.order.status, 'PARTIALLY_REFUNDED');
    assert.equal(body.order.refundedAmountCents, 3000);
  });
});
