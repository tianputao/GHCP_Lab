"""Enterprise Operations MCP Server (stdio transport, official Python MCP SDK v2).

NOTE: Never write diagnostic logs to stdout (stdout is reserved for JSON-RPC frames);
always log diagnostics to sys.stderr.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Literal

# Support direct invocation `python src/server.py` from the lab folder
LAB_ROOT = Path(__file__).resolve().parent.parent
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from src.logic import check_deploy_policy, create_reorder_draft, query_inventory  # noqa: E402

mcp = MCPServer("ghcp-lab-enterprise-ops", version="2.0.0")


@mcp.tool(
    name="query_inventory",
    description=(
        "Query enterprise hardware inventory by SKU, product name, or warehouse, "
        "and identify items below reorder threshold."
    ),
)
def query_inventory_tool(
    query: str | None = None,
    onlyLowStock: bool = False,
) -> str:
    result = query_inventory(query=query, only_low_stock=onlyLowStock)
    return json.dumps(result, indent=2)


@mcp.tool(
    name="check_deploy_policy",
    description=(
        "Evaluate whether a service deployment complies with enterprise release policies, "
        "change ticket rules, and active freeze windows."
    ),
)
def check_deploy_policy_tool(
    service: str,
    environment: Literal["dev", "staging", "production"],
    humanApprovals: int,
    securityScanPassed: bool,
    changeTicket: str | None = None,
    hasEmergencyOverride: bool = False,
) -> str:
    result = check_deploy_policy(
        service=service,
        environment=environment,
        human_approvals=humanApprovals,
        change_ticket=changeTicket,
        security_scan_passed=securityScanPassed,
        has_emergency_override=hasEmergencyOverride,
    )
    return json.dumps(result, indent=2)


@mcp.tool(
    name="create_reorder_draft",
    description=(
        "Create a non-destructive purchase reorder draft for a SKU. "
        "Never submits a real order without human confirmation."
    ),
)
def create_reorder_draft_tool(
    sku: str,
    quantity: int,
    requestedBy: str,
) -> str:
    result = create_reorder_draft(sku=sku, quantity=quantity, requested_by=requestedBy)
    return json.dumps(result, indent=2)


def main() -> None:
    print("[enterprise-ops MCP] starting stdio server", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
