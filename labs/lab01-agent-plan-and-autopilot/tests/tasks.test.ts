import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { createApp } from '../src/app.js';
import { TaskStore } from '../src/store.js';

describe('Lab 01 Task API — baseline contract', () => {
  let server: Server;
  let baseUrl: string;

  before(async () => {
    const app = createApp(new TaskStore());
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

  it('GET /health returns ok', async () => {
    const res = await fetch(`${baseUrl}/health`);
    assert.equal(res.status, 200);
    const body = (await res.json()) as { status: string };
    assert.equal(body.status, 'ok');
  });

  it('GET /tasks returns seeded tasks', async () => {
    const res = await fetch(`${baseUrl}/tasks`);
    assert.equal(res.status, 200);
    const body = (await res.json()) as { data: unknown[]; total: number };
    assert.equal(body.data.length, 25);
    assert.equal(body.total, 25);
  });

  it('POST /tasks creates and validates a task', async () => {
    const bad = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: '   ' }),
    });
    assert.equal(bad.status, 400);

    const created = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Verify Plan -> Agent loop', priority: 'high' }),
    });
    assert.equal(created.status, 201);
    const task = (await created.json()) as { id: string; title: string; priority: string };
    assert.equal(task.title, 'Verify Plan -> Agent loop');
    assert.equal(task.priority, 'high');

    const del = await fetch(`${baseUrl}/tasks/${task.id}`, { method: 'DELETE' });
    assert.equal(del.status, 204);
  });
});
