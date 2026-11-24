import { createApp } from './app.js';

const PORT = Number(process.env.PORT ?? 3001);
const app = createApp();

app.listen(PORT, () => {
  console.log(`lab01-task-api listening on http://localhost:${PORT}`);
  console.log(`  GET  http://localhost:${PORT}/health`);
  console.log(`  GET  http://localhost:${PORT}/tasks`);
  console.log(`  POST http://localhost:${PORT}/tasks`);
});
