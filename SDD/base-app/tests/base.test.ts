import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { createApp } from '../src/app.js';

describe('SDD Base App — Brownfield Order API baseline', () => {
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

  it('creates, pays, and cancels orders using standard integer cents and error envelope', async () => {
    const createRes = await fetch(`${baseUrl}/orders`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        customerId: 'cust-1',
        grossAmountCents: 10000,
        couponDiscountCents: 2000,
      }),
    });
    assert.equal(createRes.status, 201);
    const created = (await createRes.json()) as {
      id: string;
      paidAmountCents: number;
      status: string;
    };
    assert.equal(created.paidAmountCents, 8000);
    assert.equal(created.status, 'PENDING_PAYMENT');

    const payRes = await fetch(`${baseUrl}/orders/${created.id}/pay`, { method: 'POST' });
    assert.equal(payRes.status, 200);
    const paid = (await payRes.json()) as { status: string };
    assert.equal(paid.status, 'PAID');

    const cancelPaid = await fetch(`${baseUrl}/orders/${created.id}/cancel`, { method: 'POST' });
    assert.equal(cancelPaid.status, 409);
    const errBody = (await cancelPaid.json()) as { error: { code: string } };
    assert.equal(errBody.error.code, 'INVALID_ORDER_STATE');
  });
});
