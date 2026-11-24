"""Domain logic for the Lab 03 Enterprise Operations MCP Server."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypedDict, cast

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHANGE_TICKET_RE = re.compile(r"^CHG-\d{4,}$")


class InventoryItem(TypedDict):
    sku: str
    name: str
    warehouse: str
    stock: int
    reorderThreshold: int
    unitPriceCents: int


class InventoryResultItem(InventoryItem):
    needsReorder: bool


class FreezeWindow(TypedDict):
    name: str
    environments: list[str]
    active: bool
    reason: str


class EnvPolicy(TypedDict):
    minHumanApprovals: int
    requireChangeTicket: bool
    requireSecurityScan: bool


class DeployPolicies(TypedDict):
    freezeWindows: list[FreezeWindow]
    environments: dict[str, EnvPolicy]


def load_inventory() -> list[InventoryItem]:
    data = json.loads((DATA_DIR / "inventory.json").read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return cast(list[InventoryItem], data)


def load_deploy_policies() -> DeployPolicies:
    data = json.loads((DATA_DIR / "deploy-policies.json").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return cast(DeployPolicies, data)


def query_inventory(
    query: str | None = None,
    only_low_stock: bool = False,
) -> dict[str, object]:
    """Query enterprise hardware inventory by SKU, product name, or warehouse."""
    normalized = (query or "").strip().lower()
    matched: list[InventoryResultItem] = []

    for item in load_inventory():
        needs_reorder = item["stock"] <= item["reorderThreshold"]
        if only_low_stock and not needs_reorder:
            continue
        if normalized and not (
            normalized in item["sku"].lower()
            or normalized in item["name"].lower()
            or normalized in item["warehouse"].lower()
        ):
            continue
        enriched: InventoryResultItem = {**item, "needsReorder": needs_reorder}
        matched.append(enriched)

    return {"count": len(matched), "items": matched}


def check_deploy_policy(
    *,
    service: str,
    environment: str,
    human_approvals: int,
    security_scan_passed: bool,
    change_ticket: str | None = None,
    has_emergency_override: bool = False,
) -> dict[str, object]:
    """Evaluate deployment compliance against release policies and freeze windows."""
    policies = load_deploy_policies()
    env_policy = policies["environments"].get(environment)
    if env_policy is None:
        allowed_envs = ", ".join(policies["environments"].keys())
        return {
            "service": service,
            "environment": environment,
            "allowed": False,
            "blockingReasons": [f'Unknown environment "{environment}". Allowed: {allowed_envs}'],
        }

    blocking_reasons: list[str] = []

    if human_approvals < env_policy["minHumanApprovals"]:
        blocking_reasons.append(
            f"Requires at least {env_policy['minHumanApprovals']} human approval(s), got {human_approvals}."
        )

    if env_policy["requireChangeTicket"]:
        ticket = (change_ticket or "").strip()
        if not CHANGE_TICKET_RE.match(ticket):
            blocking_reasons.append("Valid change ticket (format CHG-1234) is required.")

    if env_policy["requireSecurityScan"] and not security_scan_passed:
        blocking_reasons.append("Security scan must pass before deployment.")

    for fw in policies["freezeWindows"]:
        if fw["active"] and environment in fw["environments"] and not has_emergency_override:
            blocking_reasons.append(f'Active freeze window "{fw["name"]}": {fw["reason"]}')

    return {
        "service": service,
        "environment": environment,
        "allowed": len(blocking_reasons) == 0,
        "blockingReasons": blocking_reasons,
    }


def create_reorder_draft(
    *,
    sku: str,
    quantity: int,
    requested_by: str,
) -> dict[str, object]:
    """Create a non-destructive purchase reorder draft requiring human confirmation."""
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0 or quantity > 500:
        raise ValueError("quantity must be an integer between 1 and 500")
    actor = requested_by.strip()
    if not actor:
        raise ValueError("requestedBy is required")

    target_sku = sku.strip().lower()
    matched = next((i for i in load_inventory() if i["sku"].lower() == target_sku), None)
    if matched is None:
        raise ValueError(f'SKU "{sku}" not found in inventory catalog')

    estimated_total_cents = matched["unitPriceCents"] * quantity
    return {
        "draftId": f"PO-DRAFT-{matched['sku']}-{quantity}",
        "sku": matched["sku"],
        "name": matched["name"],
        "quantity": quantity,
        "estimatedTotalCents": estimated_total_cents,
        "requiresDirectorApproval": estimated_total_cents >= 5_000_000,
        "status": "DRAFT_PENDING_HUMAN_CONFIRMATION",
        "requestedBy": actor,
    }
