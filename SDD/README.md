# SDD 独立实战实验：Vibe Coding vs Specification-Driven Development（Python + uv + OpenSpec + 12 项企业契约评测）

> **核心目标**：用同一个真实企业级 Brownfield 业务场景（**订单部分退款升级 · FastAPI**），让学员和客户在 **3 秒钟内直观看到“不用 SDD（Vibe Coding）”与“使用 SDD（OpenSpec + Agent Skills + TDD）”的本质差距**，并支持在 `playground/` 中无限次复刻动手对比（零 Node.js 硬依赖，仅装 `uv` 即可开箱跑通）。

---

## 1. 为什么选“订单部分退款”作为 SDD 标杆实验？

因为几乎所有工程师都会低估它的隐藏复杂度：
- **Vibe Coding（对照组 A：`track_a_vibe_coding/`）**：用一句常见提示词让 AI 直接写 `POST /orders/{order_id}/refunds`。代码能启动，甚至它自带的 `tests/test_basic.py` **全绿通过**！
- **但放到企业级 12 条真实金融契约（`evaluator/acceptance_suite.py`）下立刻现形**：
  1. 浮点金额精度漂移（`REQ-01`：`1968.9999999999998`）
  2. 按原价而非实付金额退款造成优惠券资损（`REQ-02`）
  3. 未支付/已取消订单被错误退款（`REQ-03`）
  4. 网络超时重试没有 `Idempotency-Key`，双倍退钱（`REQ-05`）
  5. 同一个幂等键换不同金额未报 `409 Conflict`（`REQ-06`）
  6. ≥500 元大额退款跳过人工审批（`REQ-07`）与四眼原则（`REQ-08`）
  7. 缺少必填原因与操作人校验（`REQ-09`）及不可变审计日志（`REQ-10`）
  8. 随手返回 `{ "msg": "..." }` 破坏原项目错误信封规范（`REQ-11` 架构漂移）

- **SDD（实验组 B：`track_b_sdd/`）**：先用 **OpenSpec 2.1 工件链** + `grill-me` / `SDD Architect` 固化 `proposal.md` → `specs/**/spec.md` → `design.md` → `tasks.md`，再通过 `sdd-apply-tdd` 与 `sdd-verify` 实施与反向核验，**一次性 12/12 全绿**。

---

## 2. 目录结构

```text
SDD/
├── openspec/                        # OpenSpec 2.1 工作区（内置纯 Python 严格校验 + 可选 npx 交叉校验）
│   ├── config.yaml                  # 项目上下文与不可破坏约束
│   ├── specs/orders/spec.md         # Brownfield As-Is 主规格基线
│   └── changes/add-partial-refund/  # 完整版本化 Change 工件链（proposal / specs / design / tasks）
├── .agents/skills/                  # OpenSpec 6 个官方 GitHub Copilot 技能
├── .github/
│   ├── copilot-instructions.md      # SDD 仓库宪法（Spec-First 规则）
│   ├── skills/                      # 自定义 SDD 原子技能：grill-me / sdd-apply-tdd / sdd-verify
│   └── agents/                      # BMAD 风格只读评审 Agent：SDD Architect / SDD QA Auditor
├── base_app/                        # 干净的 Brownfield 起点订单服务（无退款功能）
├── track_a_vibe_coding/             # 对照组 A：一句话 Vibe Coding 产物（自身测试全绿，企业评测大面积挂掉）
├── track_b_sdd/                     # 实验组 B：严格按 OpenSpec 实施的 SDD 产物（12/12 全绿）
├── evaluator/                       # 12 项企业契约黑盒评测引擎 & 对比评分卡
└── scripts/
    ├── validate_openspec.py         # 纯 Python 严格 OpenSpec 2.1 校验器（支持 --use-npx 叠加官方 CLI）
    └── reset_playground.py          # 重置 playground/ 给学员亲手体验 A/B 对比
```

---

## 3. 讲师 3 分钟震撼现场演示（一键可重复运行）

```bash
cd SDD

# Step 1：先运行 OpenSpec 2.1 严格校验（纯 Python 零 Node 依赖；如有 Node 可加 --use-npx 交叉校验）
uv run python scripts/validate_openspec.py

# Step 2：展示 Vibe Coding 的“假绿灯陷阱”（它自己的测试全部通过！）
uv run pytest track_a_vibe_coding/tests/test_basic.py

# Step 3：祭出 12 项企业契约“照妖镜”，当场输出 Track A vs Track B 对比评分卡！
uv run python -m evaluator.compare
```

你会看到一目了然的对比表：**Track A（Vibe Coding）在企业验收中惨败，Track B（SDD）12/12 全绿且 100% 关联 OpenSpec `REQ-01`..`REQ-12`**。

---

## 4. 学员亲手实战：在 `playground/` 里完整走一遍 Vibe → SDD 逆转

> **建议打开方式**：用 VS Code **单独打开 `SDD/` 文件夹**，即可同时识别 OpenSpec 生成的 `.agents/skills/` 以及 `.github/skills/`、`.github/agents/`。

### 第一轮：亲身体验 Vibe Coding（约 10 分钟）
1. 初始化干净的沙盒工程：
   ```bash
   uv run python scripts/reset_playground.py
   ```
2. 打开 `playground/src/app.py`，在 Copilot Chat 中故意不引用 OpenSpec，直接输入 `track_a_vibe_coding/prompt-used.md` 的模糊提示词让 Agent 实现部分退款。
3. 运行企业级评测看自己得了多少分：
   ```bash
   uv run python -m evaluator.evaluate_playground
   ```
   记录哪些隐含金融/合规要求被漏掉了。

### 第二轮：切到 SDD 完整工程流（约 20 分钟）
1. 重置沙盒回到同一起跑线：
   ```bash
   uv run python scripts/reset_playground.py
   ```
2. **需求追问（原子技能 `/grill-me`）**：在 Chat 输入：
   ```text
   /grill-me 我想给 #file:playground/src/app.py 增加部分退款能力，请先不要写代码，帮我追问并暴露所有金融精度、状态机、幂等、审批和审计边界。
   ```
3. **架构前置审阅（BMAD 只读角色 `SDD Architect`）**：在 Agent 下拉框切换到 **SDD Architect**，输入：
   ```text
   审阅 openspec/changes/add-partial-refund/ 下的 proposal.md、specs/、design.md 与 tasks.md，确认是否 READY FOR IMPLEMENTATION。
   ```
4. **按规格 TDD 实施（`/sdd-apply-tdd`）**：切回 **Copilot Agent**，输入：
   ```text
   /sdd-apply-tdd 请严格按照 openspec/changes/add-partial-refund/ 的全部规格（REQ-01..REQ-12）在 playground/src/app.py 中实现部分退款、审批与审计日志，完成后运行 uv run python -m evaluator.evaluate_playground 直到 12/12 通过。
   ```
5. **反向一致性审计（`/sdd-verify` & `SDD QA Auditor`）**：确认每条 `REQ-XX` 都有代码与测试证据、且未触碰 Non-Goals。

---

## 5. 本实验所用工具与版本

- **环境管理**：`uv` + Python 3.11+ + FastAPI + `pytest` + `mypy --strict`。
- **OpenSpec 2.1 校验**：默认由 `scripts/validate_openspec.py` 纯 Python 严格校验（零 Node.js 依赖）；如环境已装 Node.js，可加 `--use-npx` 叠加调用官方 `@fission-ai/openspec` CLI。
- **OpenSpec 内置 Copilot Skills**：`.agents/skills/openspec-{explore,propose,apply-change,update-change,sync-specs,archive-change}`。
- **自定义 SDD Skills & 只读 Agents**：`.github/skills/{grill-me,sdd-apply-tdd,sdd-verify}` + `.github/agents/{sdd-architect,sdd-qa-auditor}.agent.md`。
