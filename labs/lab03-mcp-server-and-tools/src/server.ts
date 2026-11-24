import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { checkDeployPolicy, createReorderDraft, queryInventory } from './logic.js';

/**
 * Enterprise Operations MCP Server (stdio transport).
 * NOTE: Never write diagnostic logs to stdout (stdout is reserved for JSON-RPC frames);
 * always log diagnostics to stderr.
 */
const server = new Server(
  {
    name: 'ghcp-lab-enterprise-ops',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'query_inventory',
      description:
        'Query enterprise hardware inventory by SKU, product name, or warehouse, and identify items below reorder threshold.',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Optional substring matching SKU, product name, or warehouse.',
          },
          onlyLowStock: {
            type: 'boolean',
            description: 'When true, returns only items at or below their reorder threshold.',
          },
        },
      },
    },
    {
      name: 'check_deploy_policy',
      description:
        'Evaluate whether a service deployment complies with enterprise release policies, change ticket rules, and active freeze windows.',
      inputSchema: {
        type: 'object',
        required: ['service', 'environment', 'humanApprovals', 'securityScanPassed'],
        properties: {
          service: { type: 'string', description: 'Service name being deployed.' },
          environment: {
            type: 'string',
            enum: ['dev', 'staging', 'production'],
            description: 'Target deployment environment.',
          },
          humanApprovals: { type: 'integer', minimum: 0 },
          changeTicket: { type: 'string', description: 'Change ticket ID, e.g. CHG-2048.' },
          securityScanPassed: { type: 'boolean' },
          hasEmergencyOverride: { type: 'boolean' },
        },
      },
    },
    {
      name: 'create_reorder_draft',
      description:
        'Create a non-destructive purchase reorder draft for a SKU. Never submits a real order without human confirmation.',
      inputSchema: {
        type: 'object',
        required: ['sku', 'quantity', 'requestedBy'],
        properties: {
          sku: { type: 'string' },
          quantity: { type: 'integer', minimum: 1, maximum: 500 },
          requestedBy: { type: 'string' },
        },
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;
  const payload = args as Record<string, unknown>;

  try {
    if (name === 'query_inventory') {
      const result = queryInventory(
        typeof payload.query === 'string' ? payload.query : undefined,
        Boolean(payload.onlyLowStock),
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    if (name === 'check_deploy_policy') {
      const result = checkDeployPolicy({
        service: String(payload.service ?? ''),
        environment: String(payload.environment ?? ''),
        humanApprovals: Number(payload.humanApprovals ?? 0),
        changeTicket: typeof payload.changeTicket === 'string' ? payload.changeTicket : undefined,
        securityScanPassed: Boolean(payload.securityScanPassed),
        hasEmergencyOverride: Boolean(payload.hasEmergencyOverride),
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    if (name === 'create_reorder_draft') {
      const result = createReorderDraft({
        sku: String(payload.sku ?? ''),
        quantity: Number(payload.quantity ?? 0),
        requestedBy: String(payload.requestedBy ?? ''),
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    return {
      isError: true,
      content: [{ type: 'text', text: `Unknown tool: ${name}` }],
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      isError: true,
      content: [{ type: 'text', text: `Tool execution error: ${message}` }],
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error('[enterprise-ops MCP] connected over stdio');
