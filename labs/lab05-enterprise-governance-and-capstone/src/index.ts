import { createApp } from './app.js';

const PORT = Number(process.env.PORT ?? 3005);
const app = createApp();

app.listen(PORT, () => {
  console.log(`lab05-enterprise-capstone listening on http://localhost:${PORT}`);
  console.log(`  GET http://localhost:${PORT}/health`);
  console.log(`  GET http://localhost:${PORT}/orders`);
});
