"""Real stdio end-to-end MCP client tests for Lab 03."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

LAB_ROOT = Path(__file__).resolve().parent.parent


def _extract_json(content: list[Any]) -> dict[str, Any]:
    for block in content:
        if isinstance(block, TextContent):
            parsed = json.loads(block.text)
            assert isinstance(parsed, dict)
            return parsed
    raise AssertionError(f"Expected TextContent block, got: {content!r}")


async def _run_e2e_checks() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(LAB_ROOT / "src" / "server.py")],
        cwd=str(LAB_ROOT),
    )
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # 1. Verify tool discovery
            tools_res = await session.list_tools()
            names = sorted(t.name for t in tools_res.tools)
            assert names == ["check_deploy_policy", "create_reorder_draft", "query_inventory"]

            # 2. Verify query_inventory low-stock filter
            inv_res = await session.call_tool("query_inventory", {"onlyLowStock": True})
            inv_data = _extract_json(list(inv_res.content))
            assert inv_data["count"] == 2
            skus = sorted(item["sku"] for item in inv_data["items"])
            assert skus == ["SKU-GPU-A100", "SKU-SWITCH-400G"]

            # 3. Verify check_deploy_policy blocks production during freeze window
            pol_res = await session.call_tool(
                "check_deploy_policy",
                {
                    "service": "payments-api",
                    "environment": "production",
                    "humanApprovals": 1,
                    "securityScanPassed": False,
                },
            )
            pol_data = _extract_json(list(pol_res.content))
            assert pol_data["allowed"] is False
            assert len(pol_data["blockingReasons"]) >= 3

            # 4. Verify create_reorder_draft director approval calculation
            draft_res = await session.call_tool(
                "create_reorder_draft",
                {
                    "sku": "SKU-GPU-A100",
                    "quantity": 5,
                    "requestedBy": "alice@example.com",
                },
            )
            draft_data = _extract_json(list(draft_res.content))
            assert draft_data["estimatedTotalCents"] == 6_250_000
            assert draft_data["requiresDirectorApproval"] is True
            assert draft_data["status"] == "DRAFT_PENDING_HUMAN_CONFIRMATION"


def test_mcp_server_stdio_e2e() -> None:
    asyncio.run(_run_e2e_checks())
