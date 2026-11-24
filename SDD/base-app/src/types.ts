export type OrderStatus =
  | 'PENDING_PAYMENT'
  | 'PAID'
  | 'CANCELLED'
  | 'PARTIALLY_REFUNDED'
  | 'FULLY_REFUNDED';

export interface Order {
  id: string;
  customerId: string;
  grossAmountCents: number;
  couponDiscountCents: number;
  paidAmountCents: number;
  refundedAmountCents: number;
  pendingRefundAmountCents: number;
  remainingRefundableCents: number;
  status: OrderStatus;
  createdAt: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: Array<{ field: string; message: string }>;
  };
}
