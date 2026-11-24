# GitHub Copilot 2026-11 新旧能力适配与替代方案对照表

> 核对基准：2026 年 11 月 VS Code 官方文档与 GitHub Copilot 官方文档。  
> 目的：确保本实验仓库（`GHCP_Lab`）所展示的所有高级能力均适配当前最新版本，对旧 GH-300 教材中已过时或被替代的机制给出明确替代方案。

| 旧课程/早期教材写法 | 2026-11 当前状态 | 本仓库采用的新方案 / 替代功能 | 对应实验 |
|---|---|---|---|
| **VS Code Local Harness（Extension Host）** | 正逐步弃用，能力向独立 Agent Host 迁移 | 优先选择 **Session Target = Copilot**（由共享 Copilot SDK + Agent Host 驱动，跨 VS Code / CLI / App 统一体验） | Lab 01、Lab 02 |
| **Prompt Files (`.github/prompts/*.prompt.md`)** | 与 Local Harness 绑定，官方建议迁移 | 迁移至开放标准 **Agent Skills（`.github/skills/<name>/SKILL.md`）**，支持附带脚本与资源，跨 IDE / CLI / Cloud Agent 通用 | Lab 02、SDD |
| **Custom Chat Modes (`.chatmode.md`) & 旧 `tools: [codebase]`** | 已更名或语法变更 | 使用 **`.github/agents/*.agent.md`**，Copilot schema 使用 `tools: ['read', 'search']` 与 `target: github-copilot`，弃用 `infer` | Lab 02、SDD |
| **仅靠 Instructions 约束危险操作** | 指令是概率引导，不能替代安全边界 | 新增 **Deterministic Agent Hooks（`.github/hooks/*.json` + `preToolUse` 脚本）** 实现确定性硬拦截 | Lab 02 |
| **GitHub App Copilot Extensions / Skillsets** | 已被开放协议与托管连接器取代 | 本地/企业内部系统采用 **MCP Server（`.mcp.json` / `.vscode/mcp.json`）**；常见云端 SaaS 采用 **Copilot Connectors** | Lab 03 |
| **旧版 `gh copilot suggest/explain` 扩展** | Legacy 写法 | 统一使用现代独立 **`copilot` CLI**（支持 `@file`、`/plan`、`Shift+Tab` 切换 `standard / plan / autopilot`） | Lab 01 |
| **Copilot Coding Agent** | 更名并扩展能力 | 现称 **Copilot Cloud Agent**（支持 Issues、Agents 面板、VS Code Cloud Target 与 CLI `/delegate`） | Lab 01 |
| **Code Review 仅限 GitHub.com** | 过时说法 | 现已同时支持 **VS Code 本地即时 Review**（Source Control Changes 面板）与 **GitHub PR `@copilot` Review**（可按仓库规则开启自动评审） | Lab 04 |
| **Premium Request Units (PRUs) + 降级回退** | 已于 2026-06-01 切换 | 全面采用 **GitHub AI Credits**（按实际 token 计费，Business/Enterprise 组织池化 + 四级预算控制，无旧版自动回退） | Lab 05 |
| **GitHub Spark (`github.com`)** | 已于 **2026-08-31 退役** | 本实验仓库已彻底移除 Spark 相关内容，改以 Agent Mode + SDD 工程闭环替代 | 全局 |
| **依赖原生 C++ 插件（如 `better-sqlite3`）** | 复制到不同 OS / Node 架构易编译失败 | Lab 04 改用 **Node 22.5+/24 内置 `node:sqlite`**，实现 100% 跨平台零原生编译运行真实 SQL 注入演示 | Lab 04 |
