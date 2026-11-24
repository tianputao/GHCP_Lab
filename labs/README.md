# GitHub Copilot 高级能力实战实验室（Labs 01–05）

本目录收录了 5 个彼此解耦、可独立运行与重置的进阶实验（**已剔除基础 Inline Suggestion 等入门内容**，并按 2026-11 最新产品形态完成替换与升级）。

## 实验路线图

| 编号 | 目录 | 核心高级能力 | 预计时长 | 独立验证命令 |
|---|---|---|---|---|
| **Lab 01** | [lab01-agent-plan-and-autopilot](lab01-agent-plan-and-autopilot/README.md) | Plan → Agent / Autopilot、Task-Aware Auto、Copilot CLI、Cloud Agent 委派 | 25–35 min | `npm --prefix labs/lab01-agent-plan-and-autopilot run verify` |
| **Lab 02** | [lab02-customization-skills-hooks](lab02-customization-skills-hooks/README.md) | 全局/路径 Instructions、**2026 Agent Skills**、只读 Custom Agent、**确定性 Hooks**、Copilot Spaces | 30–40 min | `npm --prefix labs/lab02-customization-skills-hooks run verify` |
| **Lab 03** | [lab03-mcp-server-and-tools](lab03-mcp-server-and-tools/README.md) | **自建企业 stdio MCP Server**（替代旧 Extensions/Skillsets）+ 真实协议 E2E 测试 | 25–30 min | `npm --prefix labs/lab03-mcp-server-and-tools run verify` |
| **Lab 04** | [lab04-testing-security-and-review](lab04-testing-security-and-review/README.md) | AI TDD、假测试识破、真实 SQLite SQL 注入与 `eval()` 攻防、Code Review & CodeQL Autofix | 25–35 min | `npm --prefix labs/lab04-testing-security-and-review run verify` |
| **Lab 05** | [lab05-enterprise-governance-and-capstone](lab05-enterprise-governance-and-capstone/README.md) | Content Exclusions、IP Indemnity、Audit API、**GitHub AI Credits 成本优化** & 8 步 Capstone | 30–40 min | `npm --prefix labs/lab05-enterprise-governance-and-capstone run verify` |

> **提示**：做 Lab 02 和 Lab 03 时，推荐在 VS Code 中**单独打开对应子文件夹**，让工作区级的 `.github/`、`.mcp.json` 和 `.vscode/mcp.json` 自动精准生效。
