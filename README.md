# GHCP_Lab · GitHub Copilot 高级实战与 SDD 独立实验仓库（Python + uv 版）

> 一个**完全独立、可编程验证、可复制离线展示、同时支持云端 GitHub 联动**的 GitHub Copilot 高级能力实战仓库（**100% Python + `uv` 环境管理**，对齐 **2026-11** 最新产品形态，剔除基础 Inline Suggestion 入门演示；原 TypeScript 版本已归档保留在 `TS` 分支）。  
> 远端仓库：`https://github.com/tianputao/GHCP_Lab`

---

## 仓库结构（两大独立实验板块）

```text
GHCP_Lab/
├── README.md                                  # 本总指南
├── COMPATIBILITY-2026.md                      # 2026-11 新旧功能替代与迁移对照表
├── pyproject.toml & uv.lock                   # uv Workspace 统一环境与锁定依赖（零手动配 venv）
├── scripts/run_all.py                         # 一键全量验收、测试、SDD 对比与重置编排器
├── .github/
│   ├── workflows/ci.yml                       # GitHub Actions (uv) 自动验证全部 6 个子工程
│   ├── workflows/codeql.yml                   # Lab 04 CodeQL (Python) + Copilot Autofix 云端安全扫描
│   ├── ISSUE_TEMPLATE/                        # 供 Cloud Agent 与 SDD 委派实验使用的 Issue 模板
│   └── pull_request_template.md               # 含 Responsible AI 披露模板
│
├── labs/                                      # 【板块一】GitHub Copilot 高级能力实战（5 个独立子工程）
│   ├── README.md                              # Labs 01–05 导览
│   ├── lab01-agent-plan-and-autopilot/        # FastAPI · Plan -> Agent/Autopilot、Task-Aware Auto、CLI & Cloud Agent
│   ├── lab02-customization-skills-hooks/      # 纯标准库 Python · Instructions、2026 Agent Skills、只读 Agent、确定性 Hooks、Spaces
│   ├── lab03-mcp-server-and-tools/            # 官方 Python mcp SDK · 自建企业 stdio MCP Server（替代旧 Extensions/Skillsets）
│   ├── lab04-testing-security-and-review/     # Python 内置 sqlite3 · AI TDD、假测试识破、真实 SQLi & eval()、Code Review & Autofix
│   └── lab05-enterprise-governance-and-capstone/ # FastAPI · Content Exclusions、IP Indemnity、AI Credits 优化 & 8步 Capstone
│
└── SDD/                                       # 【板块二】独立 SDD 深度对比实验（Vibe Coding vs OpenSpec · FastAPI）
    ├── README.md                              # 3 分钟讲师震撼演示 + 30 分钟学员 Playground 实战手册
    ├── openspec/                              # 真实 OpenSpec 2.1 工件链（内置纯 Python 严格校验 + 可选 npx 交叉校验）
    ├── .agents/skills/ & .github/             # OpenSpec 官方技能 + grill-me / sdd-apply-tdd / sdd-verify + 只读评审 Agent
    ├── base_app/                              # Brownfield 干净起点
    ├── track_a_vibe_coding/                   # 对照组 A（自身测试全绿，企业 12 项契约惨败）
    ├── track_b_sdd/                           # 实验组 B（严格按 SDD 实施，12/12 全绿 + 100% REQ 追溯）
    └── evaluator/                             # 自动化黑盒验收对比评分卡
```

---

## 环境前置要求

- **仅需安装 [`uv`](https://docs.astral.sh/uv/getting-started/installation/)**（`uv` 会按 `.python-version` 自动下载并管理 Python 3.12 虚拟环境，学员无需手工装 Python、conda 或 Node.js！）
  - macOS / Linux：`curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows PowerShell：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- **VS Code**（最新稳定版）+ **GitHub Copilot** 扩展 + **Python** 扩展
- **可选（云端/CLI 演示）**：GitHub CLI（`gh`）与独立 `copilot` CLI；付费 Copilot 计划（体验 Cloud Agent / Spaces / Code Review）

---

## 1 分钟快速验收与一键命令（克隆即跑通）

```bash
# 1. 克隆仓库并进入目录
git clone https://github.com/tianputao/GHCP_Lab.git
cd GHCP_Lab

# 2. 一键同步全部 6 个子工程依赖（uv 自动准备好 Python 3.12 与 .venv）
uv sync --all-packages

# 3. 一键运行全部 6 个子工程的 mypy 静态类型检查、pytest 测试、MCP 协议 E2E 测试、Hook 测试、OpenSpec 严格校验与 SDD 对比评分卡
uv run ghcp-lab verify

# 4. 单独运行最具震撼力的 SDD vs Vibe Coding 对比评分卡
uv run ghcp-lab sdd-compare

# 5. 演示结束后一键还原 Lab 02 干净态 & 重置 SDD/playground/
uv run ghcp-lab reset
```

---

## 推荐演示 / 学员动手顺序

### 路线一：GitHub Copilot 高级工程能力（2–3 小时）
1. **[Lab 01 · Plan / Agent / Autopilot / Cloud Agent](labs/lab01-agent-plan-and-autopilot/README.md)**：体验 Plan → 人工审批 → Agent/Autopilot 闭环、Task-Aware Auto，并用 `.github/ISSUE_TEMPLATE/cloud-agent-task.yml` 在 `tianputao/GHCP_Lab` 上实测 Cloud Agent。
2. **[Lab 02 · 2026 定制化全家桶](labs/lab02-customization-skills-hooks/README.md)**：单独打开该文件夹，完整走一遍 Before→After 全局/路径指令、**Agent Skills（带 Python 规范校验脚本）**、只读安全审查 Agent、**确定性 `preToolUse` Python Hooks 拦截危险命令**、以及 GitHub Copilot Spaces。
3. **[Lab 03 · 自建企业 MCP Server](labs/lab03-mcp-server-and-tools/README.md)**：单独打开该文件夹，通过 `uv run python src/server.py` 启动 `enterprise-ops` stdio MCP Server，用 Agent 调用库存查询、发布封网策略检查和采购草稿工具。
4. **[Lab 04 · AI 测试质量、OWASP 安全攻防与 Code Review](labs/lab04-testing-security-and-review/README.md)**：识破同义反复假测试，用真实 SQL 注入载荷 `' OR '1'='1' --` 验证 Python `sqlite3` 漏洞与参数化修复，体验 VS Code 本地 + GitHub PR `@copilot` Review 及 CodeQL（Python）Autofix。
5. **[Lab 05 · 企业治理、AI Credits 成本优化与 Capstone](labs/lab05-enterprise-governance-and-capstone/README.md)**：运行 `token_budget_audit.py` 量化上下文省 Token 收益，完成 Content Exclusions、审计 API 与 8 步企业闭环。

### 路线二：SDD 规格驱动开发专题（45–60 分钟）
- 直接进入 **[SDD/README.md](SDD/README.md)**：
  - 先跑 `uv run ghcp-lab sdd-compare` 展示 Vibe Coding“自身测试全绿但企业 12 项契约大面积踩坑” vs SDD“OpenSpec + Skills + TDD 一次性 12/12 全绿”；
  - 再用 VS Code 单独打开 `SDD/` 目录，在 `playground/` 中带学员亲手完成从 Vibe Coding 到 `/grill-me` → `SDD Architect` → `/sdd-apply-tdd` → `/sdd-verify` 的完整逆转！

---

## 离线拷贝与跨机展示说明

- 整个仓库**纯 Python + `uv` 零 Node.js 硬依赖**，并自带锁定的 `uv.lock`；学员在 Windows / macOS / Linux 克隆后，执行 `uv sync --all-packages && uv run ghcp-lab verify` 即可开箱跑通全部本地实验与对比评测。
- 每个子工程都带有独立的 `pyproject.toml`，既支持在根目录统一运行，也支持把单个子工程独立拷贝出去运行。
- 云端能力（Cloud Agent、Code Review、CodeQL Autofix、Copilot Spaces）已全部预先配置好模板、Workflow 与知识库文档，推送到 `https://github.com/tianputao/GHCP_Lab` 即可直接演示。
- 详细的新旧功能替代说明请先阅读 **[COMPATIBILITY-2026.md](COMPATIBILITY-2026.md)**。
