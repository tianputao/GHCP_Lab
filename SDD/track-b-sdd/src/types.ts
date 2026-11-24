import type { Order } from '../../base-app/src/types.js';

export type RefundStatus = 'COMPLETED' | 'PENDING_APPROVAL';

export interface RefundRecord {
  id: string;
  orderId: string;
  amountCents: number;
  reason: string;
  actorId: string;
  approverId?: string;
  status: RefundStatus;
  idempotencyKey: string;
  createdAt: string;
  completedAt?: string;
}

export type AuditEventType =
  | 'REFUND_COMPLETED'
  | 'REFUND_PENDING_APPROVAL'
  | 'REFUND_APPROVED';

export interface AuditEvent {
  id: string;
  eventType: AuditEventType;
  orderId: string;
  refundId: string;
  actorId: string;
  amountCents: number;
  reason: string;
  timestamp: string;
}

export interface RefundResponsePayload {
  refund: RefundRecord;
  order: Order;
  idempotentReplay: boolean;
}
