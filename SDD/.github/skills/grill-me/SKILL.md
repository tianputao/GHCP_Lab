---
name: grill-me
description: "Interrogate a vague feature request BEFORE writing code to surface hidden assumptions, edge cases, state transitions, financial precision, security/approval rules, and explicit non-goals. Use before creating an OpenSpec proposal or whenever a requirement feels under-specified."
---

# Grill-Me — Pre-Code Assumption Interrogator (SDD Atomic Skill)

## Goal
Prevent **Vibe Coding drift** by turning a vague 1-sentence request into crystal-clear, testable engineering decisions BEFORE a single line of production code is written.

## Protocol
When the user proposes a feature or change:
1. **Do NOT write implementation code yet.**
2. Inspect the existing codebase (`base_app/` or `playground/`) to identify existing conventions (error envelope, types, state machines, monetary units).
3. Ask focused, high-leverage questions grouped into 6 risk buckets (max 2 questions per bucket):
   - **Data & Precision**: Monetary units (integer cents vs decimal)? Rounding/caps? Coupon/discount proration?
   - **Lifecycle & State Machine**: Which states allow this action? What states does it transition to?
   - **Idempotency & Concurrency**: How are retries deduplicated? What if the same key carries a different payload?
   - **Governance & Risk Thresholds**: Are high-value operations auto-executed or routed to human approval (four-eyes)?
   - **Audit & Observability**: What immutable events and actor metadata must be recorded?
   - **Explicit Non-Goals**: What must NOT change in the brownfield system?
4. Summarize confirmed answers into a draft **Requirements Table (`REQ-01`..`REQ-NN`)** with `WHEN / THEN` acceptance criteria ready for `openspec/changes/<name>/specs/`.
