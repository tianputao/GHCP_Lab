import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.resolve(__dirname, '../data');

export interface InventoryItem {
  sku: string;
  name: string;
  warehouse: string;
  stock: number;
  reorderThreshold: number;
  unitPriceCents: number;
}

export interface DeployPolicies {
  freezeWindows: Array<{
    name: string;
    environments: string[];
    active: boolean;
    reason: string;
  }>;
  environments: Record<
    string,
    {
      minHumanApprovals: number;
      requireChangeTicket: boolean;
      requireSecurityScan: boolean;
    }
  >;
}

export function loadInventory(): InventoryItem[] {
  return JSON.parse(readFileSync(path.join(DATA_DIR, 'inventory.json'), 'utf8')) as InventoryItem[];
}

export function loadDeployPolicies(): DeployPolicies {
  return JSON.parse(readFileSync(path.join(DATA_DIR, 'deploy-policies.json'), 'utf8')) as DeployPolicies;
}

export function queryInventory(query?: string, onlyLowStock = false): {
  count: number;
  items: Array<InventoryItem & { needsReorder: boolean }>;
} {
  const normalized = (query ?? '').trim().toLowerCase();
  const matched = loadInventory()
    .map((item) => ({
      ...item,
      needsReorder: item.stock <= item.reorderThreshold,
    }))
    .filter((item) => {
      if (onlyLowStock && !item.needsReorder) return false;
      if (!normalized) return true;
      return (
        item.sku.toLowerCase().includes(normalized) ||
        item.name.toLowerCase().includes(normalized) ||
        item.warehouse.toLowerCase().includes(normalized)
      );
    });

  return { count: matched.length, items: matched };
}

export function checkDeployPolicy(input: {
  service: string;
  environment: string;
  humanApprovals: number;
  changeTicket?: string;
  securityScanPassed: boolean;
  hasEmergencyOverride?: boolean;
}): {
  service: string;
  environment: string;
  allowed: boolean;
  blockingReasons: string[];
} {
  const policies = loadDeployPolicies();
  const envPolicy = policies.environments[input.environment];
  if (!envPolicy) {
    return {
      service: input.service,
      environment: input.environment,
      allowed: false,
      blockingReasons: [`Unknown environment "${input.environment}". Allowed: ${Object.keys(policies.environments).join(', ')}`],
    };
  }

  const blockingReasons: string[] = [];

  if (input.humanApprovals < envPolicy.minHumanApprovals) {
    blockingReasons.push(
      `Requires at least ${envPolicy.minHumanApprovals} human approval(s), got ${input.humanApprovals}.`,
    );
  }

  if (envPolicy.requireChangeTicket) {
    const ticket = (input.changeTicket ?? '').trim();
    if (!/^CHG-\d{4,}$/.test(ticket)) {
      blockingReasons.push('Valid change ticket (format CHG-1234) is required.');
    }
  }

  if (envPolicy.requireSecurityScan && !input.securityScanPassed) {
    blockingReasons.push('Security scan must pass before deployment.');
  }

  for (const fw of policies.freezeWindows) {
    if (fw.active && fw.environments.includes(input.environment) && !input.hasEmergencyOverride) {
      blockingReasons.push(`Active freeze window "${fw.name}": ${fw.reason}`);
    }
  }

  return {
    service: input.service,
    environment: input.environment,
    allowed: blockingReasons.length === 0,
    blockingReasons,
  };
}

export function createReorderDraft(input: {
  sku: string;
  quantity: number;
  requestedBy: string;
}): {
  draftId: string;
  sku: string;
  name: string;
  quantity: number;
  estimatedTotalCents: number;
  requiresDirectorApproval: boolean;
  status: 'DRAFT_PENDING_HUMAN_CONFIRMATION';
  requestedBy: string;
} {
  if (!Number.isInteger(input.quantity) || input.quantity <= 0 || input.quantity > 500) {
    throw new Error('quantity must be an integer between 1 and 500');
  }
  const actor = input.requestedBy.trim();
  if (!actor) {
    throw new Error('requestedBy is required');
  }
  const item = loadInventory().find((i) => i.sku.toLowerCase() === input.sku.trim().toLowerCase());
  if (!item) {
    throw new Error(`SKU "${input.sku}" not found in inventory catalog`);
  }

  const estimatedTotalCents = item.unitPriceCents * input.quantity;
  return {
    draftId: `PO-DRAFT-${item.sku}-${input.quantity}`,
    sku: item.sku,
    name: item.name,
    quantity: input.quantity,
    estimatedTotalCents,
    requiresDirectorApproval: estimatedTotalCents >= 5_000_000,
    status: 'DRAFT_PENDING_HUMAN_CONFIRMATION',
    requestedBy: actor,
  };
}
