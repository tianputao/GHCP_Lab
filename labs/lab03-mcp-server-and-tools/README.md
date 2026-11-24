# Lab 03 · 自建企业 MCP Server（替代旧 Copilot Extensions / Skillsets）

> **2026 架构演进**：传统 GH-300 课程中的 GitHub App Copilot Extensions / Skillsets 已被开放标准 **MCP（Model Context Protocol）** 与 **Copilot Connectors** 取代。本实验提供一个**完整可运行、带真实 stdio 协议集成测试**的企业运维 MCP Server。  
> **建议打开方式**：用 VS Code 单独打开本目录 `labs/lab03-mcp-server-and-tools/`，VS Code 会自动发现 `.mcp.json`（Copilot Agent Host / CLI 标准）和 `.vscode/mcp.json`（编辑器工作区标准）。

---

## 0. 验证 MCP Server 端到端协议握手

```bash
cd labs/lab03-mcp-server-and-tools
npm run verify   # 自动拉起 stdio MCP Server 子进程并调用全部 3 个工具做断言测试
```

你会看到端到端测试完成：
- `query_inventory`：筛选低于补货阈值的库存项（`SKU-GPU-A100`、`SKU-SWITCH-400G`）
- `check_deploy_policy`：校验生产发布审批人数、变更单、安全扫描与月结封网窗口
- `create_reorder_draft`：生成需人工确认的采购草稿并计算总监审批阈值

---

## 练习 1：在 VS Code Copilot 中加载并调用本机 MCP Server

1. 用 VS Code 打开 `labs/lab03-mcp-server-and-tools/`。
2. 打开命令面板运行 **Chat: Open Customizations → MCP Servers**（或打开 `.mcp.json` / `.vscode/mcp.json` 点击上方 **Start**），确认 `enterprise-ops` 状态为 Running。
3. 在 Copilot Chat（选择 **Copilot** 目标与 **Agent/Interactive** 模式）提问：
   ```text
   帮我查一下目前有哪些低库存的硬件 SKU，然后给库存为 0 的那一款生成一份补货 10 台的采购草稿（申请人写 zhangsan@corp.example），最后评估如果今晚把 payments-api 发布到 production（目前只有 1 个审批人，安全扫描已通过，变更单 CHG-2026）是否合规。
   ```
4. **安全审批观察点**：
   - 每次 MCP 工具调用都会触发权限确认对话框，请展开参数确认无误后再点 Allow；
   - 观察 `create_reorder_draft` 刻意设计为“只生成 `DRAFT_PENDING_HUMAN_CONFIRMATION` 草稿，不直接下单”，体现企业 Agent 工具的**非破坏性设计原则**。

---

## 练习 2：扩展一个新工具（Agent 实战）

让 Copilot Agent 为 `src/logic.ts` 与 `src/server.ts` 新增第 4 个工具 `estimate_restock_budget`（汇总所有低库存 SKU 补齐到 `reorderThreshold * 2` 所需的总预算分值），并补充一条 `tests/mcp-client.test.ts` 端到端测试，然后运行 `npm run verify`。

---

## 工程最佳实践备忘

- **永远不要在 stdio MCP Server 中调用 `console.log()`**：`stdout` 专用于 JSON-RPC 帧，诊断日志一律走 `console.error()`（`stderr`）。
- **两份配置文件的分工**：`.mcp.json` 面向 Copilot Agent Host / Copilot CLI（键名为 `mcpServers`）；`.vscode/mcp.json` 面向 VS Code Local 编辑器扩展（键名为 `servers`）。
