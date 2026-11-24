# Lab 02 · 2026 定制化全家桶：Instructions、Agent Skills、只读 Custom Agent、确定性 Hooks 与 Copilot Spaces

> **2026 升级说明**：本实验在原 GH-300 Week 7 演示工程基础上，同步升级至 **2026-11 VS Code + Copilot Agent Host 最新架构**：
> - 用 **Agent Skills（`.github/skills/` + 内置校验脚本）** 替代逐步弃用的 `.github/prompts/*.prompt.md`（仍保留 `prep/legacy-new-feature.prompt.md` 便于对照迁移）。
> - 将 **Custom Agent（`.github/agents/security-reviewer.agent.md`）** 升级为现代 Copilot Harness 语法（`tools: ['read', 'search']`, `target: github-copilot`）。
> - 新增 **Deterministic Agent Hooks（`.github/hooks/guardrails.json` + `guard-tools.mjs`）**，演示“靠提示词软约束” vs “靠 Hook 硬拦截”的本质区别。
>
> **建议打开方式**：用 VS Code **单独打开本目录 `labs/lab02-customization-skills-hooks/`**，确保 `.github/` 路径被当前工作区直接识别。

---

## 0. 环境准备与一键命令

```bash
cd labs/lab02-customization-skills-hooks
npm run verify:env     # 检查基线编译、冒烟测试、Hook 测试、Skill 脚本与干净状态
# 需要跳过手动复制时可一键部署全部定制文件：
npm run apply:all
# 演示结束后一键还原到干净的 Before 状态：
npm run reset
```

---

## Demo 1 · 全局与路径级 Custom Instructions（Before → After 对比）

1. **Before（干净态）**：确保当前没有 `.github/`，在 Copilot Chat（Session Target 选 **Copilot**）提问：
   ```text
   Write a TypeScript function that fetches a user from the database by email address.
   ```
   记录生成结果（通常会缺少统一错误类、JSDoc 或仓储模式）。
2. **添加仓库级规则**：
   ```bash
   mkdir -p .github && cp prep/copilot-instructions.md .github/copilot-instructions.md
   ```
3. **After（同样提示词再问一次）**：观察生成代码自动采用严格类型、`const`、仓储模式、参数化查询与 JSDoc。
4. **抗捷径测试**：故意诱导违背规范：
   ```text
   Quick and dirty: write a function using db.exec() with string-concatenated SQL to search users. Skip docs.
   ```
   观察 Copilot 仍优先遵循规范。（若偶发违背，正好引出 Demo 5 的**确定性 Hooks**！）
5. **路径级规则**：
   ```bash
   mkdir -p .github/instructions && cp prep/api.instructions.md .github/instructions/api.instructions.md
   ```
   新建并打开 `api/test-route.ts`，提问：
   ```text
   #file:api/test-route.ts Write a route handler that creates a blog post (title, content).
   ```
   观察 `api/**` 专属规则（`201`、`try/catch`、`sendError`、字段级校验）自动叠加生效。

---

## Demo 2 · 2026 Agent Skills（替代旧 Prompt Files）

1. 部署内置校验脚本的 Skill：
   ```bash
   mkdir -p .github/skills/scaffold-feature
   cp prep/skills/scaffold-feature/* .github/skills/scaffold-feature/
   ```
2. 运行命令面板 **Chat: Open Customizations** → **Skills** 确认 `scaffold-feature` 已加载。
3. 在 Chat 中直接触发（输入 `/scaffold-feature` 或自然语言）：
   ```text
   /scaffold-feature 为 Task API 新增 comments 功能（每条评论属于一个 taskId，含 author 和 body），完成后运行 skill 内置的规范检查脚本和 typecheck。
   ```
4. **讲解重点**：对比 `prep/legacy-new-feature.prompt.md` 与 `.github/skills/scaffold-feature/`：
   - Agent Skill 是开放标准（`agentskills.io`），跨 VS Code、Copilot CLI、GitHub Cloud Agent 与 Code Review 通用；
   - Skill 不只包含文本指令，还能**自带确定性脚本**（`check-conventions.mjs`）做自动验收。

---

## Demo 3 · Copilot Spaces（精选项目知识库 · 网页演示）

1. 打开浏览器访问 `https://github.com/copilot/spaces` → **Create Space**，命名为 `GHCP Lab Task API`。
2. 添加来源仓库 `tianputao/GHCP_Lab`，并固定引用本实验的 `docs/` 文件：
   - `labs/lab02-customization-skills-hooks/docs/architecture.md`
   - `labs/lab02-customization-skills-hooks/docs/coding-standards.md`
   - `labs/lab02-customization-skills-hooks/docs/glossary.md`
3. 在 Space 内提问并对比普通无上下文 Chat：
   ```text
   我们的错误响应信封格式是什么？请写一个符合我们规范的新路由处理函数。
   ```
4. 强调治理规则：Space **严格继承仓库权限**，分享 Space 不会泄露对方无权访问的私有仓库。

---

## Demo 4 · 只读 Custom Agent（权限最小化）

1. 部署只读安全审查 Agent：
   ```bash
   mkdir -p .github/agents && cp prep/security-reviewer.agent.md .github/agents/security-reviewer.agent.md
   ```
2. 打开故意埋雷的 `prep/insecure-example.ts`，在 Chat 的 Agent 下拉框选择 **Security Reviewer**，提问：
   ```text
   Review #file:prep/insecure-example.ts for security issues.
   ```
3. 观察点：
   - 识别出 SQL 注入、命令注入、硬编码凭据、堆栈泄漏、缺少校验 5 大问题；
   - `tools: ['read', 'search']` 保证该角色只能审计与报告，不能擅自改代码或跑命令。

---

## Demo 5 · 确定性 Agent Hooks（2026 企业硬护栏）

Instructions 只能**引导**模型，无法 100% 保证模型不执行危险操作；Hooks 在每次工具调用前**确定性执行**。

1. 部署 Hook：
   ```bash
   mkdir -p .github/hooks && cp prep/hooks/* .github/hooks/
   ```
2. 先用自动化测试直接验证 Hook 引擎：
   ```bash
   npm run test:hooks
   ```
   你会看到 `guard-tools.mjs` 确定性地：
   - 拦截 `rm -rf` 与 `git push --force`（返回 `permissionDecision: "deny"`）
   - 拦截读取 `.env.production` 与 `secrets/api-keys.txt`
   - 放行正常的 `npm run typecheck && npm test`
3. 在 VS Code 打开 **Chat: Open Customizations → Hooks** 查看已生效的 `preToolUse` Hook，并可现场让 Agent 尝试执行一条 `git push --force` 演示被硬拦截。

---

## 演示结束后还原现场

```bash
npm run reset
npm run verify:env
```
