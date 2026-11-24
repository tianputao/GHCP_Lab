# Lab 05 · 企业治理、AI Credits 成本优化与全链路 Capstone 实战

> **对应高级能力**：Content Exclusions 内容排除、Duplication Detection 与 IP Indemnity、Audit Logs / Seat API、Token-Based Billing（GitHub AI Credits）上下文省流优化，以及把所有能力串成一条线的 8 步企业 Capstone。

---

## 0. 验证基线与内置审计工具

```bash
cd labs/lab05-enterprise-governance-and-capstone
npm run verify   # 编译 + 冒烟测试 + Token 上下文优化审计 + 治理 API 模板检查
```

---

## 8 步企业全链路演练

### Step 1 · 方案选型与治理模型（Business vs Enterprise）
- 确认企业核心治理诉求：组织级策略级联（Enterprise → Org → Repo）、Content Exclusions、Duplication Detection（**必须开启 Blocked 才能享有微软 IP Indemnity**）、Audit Logs 接入 SIEM、SAML SSO / SCIM 席位自动回收。

### Step 2 · Content Exclusions 内容排除
- 阅读 `.github/CONTENT-EXCLUSIONS.md` 并查看本实验预置的假密钥文件 `.env.example` 与 `secrets/api-keys.txt`。
- 若有 Business / Enterprise 测试组织，在 GitHub 设置中配置排除规则（最长需 30 分钟生效），随后验证排除行为，并结合 **Lab 02 的确定性 Hooks** 做到纵深防御。

### Step 3 · 审阅仓库级 Custom Instructions
- 打开 `.github/copilot-instructions.md`，确认其字数控制在 Copilot Code Review 的 **4,000 字符有效窗口**以内（通过 `npm run audit:tokens` 自动校验）。

### Step 4 · Token-Based Billing（GitHub AI Credits）上下文优化实战
运行内置分析工具：
```bash
npm run audit:tokens
```
观察输出并实践四条省 Credits 黄金法则：
1. 用精准 `#file` 引用代替全仓库无边界扫描（避免每轮重复输入数万无用 Token）；
2. 保持 `.github/copilot-instructions.md` 精炼高密度，提升 Prompt Caching 命中率；
3. 默认采用 **Task-Aware Auto** 路由，仅在高价值推理场景手动切重模型；
4. 先用局部单测/类型检查快速收敛，再跑全量构建与评审。

### Step 5 · Agent Mode 实现 `POST /orders` + 自动化测试
打开 `src/routes/orders.ts` 中的 `TODO` 块，切换到 Copilot **Plan → Agent Mode**：
```text
根据 #file:src/routes/orders.ts 中的 TODO 与 #file:.github/copilot-instructions.md 规范，
先给出计划，再实现 POST /orders，并在 #file:tests/orders.smoke.test.ts 补充正常创建（201）与非法参数（400）测试，最后运行 npm run verify。
```

### Step 6 · 修复同义反复假测试（Tautological Test）
打开 `tests/discount.test.ts`，识别为何 `applyDiscount(100, '10')` 和自己比较毫无价值，改写为硬编码预期值（如 `90`、边界 `0`、`100` 及非法输入报错）。

### Step 7 · 发现并修复 `eval()` 代码注入漏洞（OWASP A03）
打开 `src/lib/discount.ts`，让 Copilot 审计并移除 `eval(rule)`，替换为严格数值解析与范围校验，运行 `npm test` 验证。

### Step 8 · 审计 API 检查与 Responsible AI PR 披露
- （若有组织管理员权限）运行：
  ```bash
  bash scripts/check-org-governance.sh <YOUR-ORG-NAME>
  ```
- 提交 PR 时按仓库根目录 `.github/pull_request_template.md` 填写 **Responsible AI Disclosure**，声明 AI 协助范围与人类审查责任。
