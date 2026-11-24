# Lab 04 · AI 辅助测试、OWASP 安全攻防、Copilot Code Review 与 CodeQL Autofix

> **对应高级能力**：Agent 驱动 TDD、识别同义反复假测试（Tautological Tests）、真实 SQL 注入与 `eval()` 代码注入攻防验证、IDE 本地与 GitHub PR Copilot Code Review、CodeQL + Copilot Autofix。  
> **跨平台亮点**：使用 Node 22.5+/24 内置 `node:sqlite`，**无需编译 C++ 原生扩展**，复制到任何电脑都能直接跑通真实 SQLite 注入实验。

---

## 0. 运行基线与攻防证明

```bash
cd labs/lab04-testing-security-and-review
npm run verify
```

观察输出：
- `tests/security.attack-vector.test.ts` 用真实 SQL 注入载荷 `' OR '1'='1' --` 证明 `searchUsersVulnerable` 会把 `superadmin` 全部拖库，而参数化查询 `searchUsersSafe` 返回 `0` 条；
- 同时证明 `applyDiscountVulnerable` 会执行任意表达式（`5 + 5`），而 `applyDiscountSafe` 会严格拒绝。

---

## 练习 1：识破“假绿灯”测试（Tautological Tests）+ Agent TDD

1. 打开 `tests/discount.test.ts`，选中第一条测试，问 Copilot Chat：
   ```text
   为什么第一条测试虽然能通过，但在工程上是危险的无效测试？请用一段带 bug 的实现举例说明它为何无法发现回归。
   ```
2. **TDD 实战**：先不要改实现，在 `tests/discount.test.ts` 中让 Copilot 为 `calculateDiscount` 补充新需求测试（红灯）：
   ```text
   我想给 calculateDiscount 增加第 5 个可选参数 vipBonusPercent（默认 0，额外叠加折扣但总折扣不超过 maxCap 且不超 amount）。
   请先按 TDD 原则在 tests/discount.test.ts 写 4 条硬编码预期值的失败测试（先别改 src/），运行 npm test 确认红灯；
   确认红灯后再修改 src/calculateDiscount.ts 让测试全部变绿。
   ```

---

## 练习 2：OWASP 安全审计与攻击向量测试

1. 打开 `src/userSearchSqlDemo.ts` 和 `src/discountEvalBug.ts`，选中漏洞函数，让 Copilot Chat 扮演安全工程师审计：
   ```text
   #file:src/userSearchSqlDemo.ts #file:src/discountEvalBug.ts
   请按 OWASP Top 10 列出漏洞类别、严重级别、攻击载荷、影响和最小修复方案。
   ```
2. 动手将 `searchUsersVulnerable` 和 `applyDiscountVulnerable` 改造为安全实现，并把 `tests/security.attack-vector.test.ts` 更新为验证改造后的函数全部拒绝攻击载荷。

---

## 练习 3：体验双端 Copilot Code Review（VS Code 本地 + GitHub PR）

### A. VS Code 本地即时 Code Review（2026 已原生支持）
1. 修改 `src/discountEvalBug.ts` 保留一点小缺陷（例如漏掉负数检查）。
2. 在 VS Code 左侧 **Source Control** 的 Changes 面板点击 **Copilot Code Review** 图标（或选中代码右键 **Generate Code → Review**）。
3. 审阅行内建议，体验 **Apply / Discard**（不会自动 commit）。

### B. GitHub.com PR 自动 Code Review
1. 在 `tianputao/GHCP_Lab` 上新建分支并推送一笔小改动创建 PR：
   ```bash
   gh pr create --repo tianputao/GHCP_Lab --title "Lab 04 security fix" --reviewer @copilot
   ```
2. 观察 Copilot 在 PR 中输出的 High/Medium/Low 严重度评审意见，体验 **Fix with Copilot** 或重新请求评审。

---

## 练习 4：CodeQL + Copilot Autofix（云端安全扫描）

本仓库根目录下已经预置了 `.github/workflows/codeql.yml`：
1. 推送到 `https://github.com/tianputao/GHCP_Lab` 后，打开仓库 **Actions** 页签确认 `CodeQL Security Scan` 运行完成。
2. 进入仓库 **Security → Code scanning alerts** 查看扫描出的 `eval()` / SQL 注入告警。
3. 点击具体告警中的 **Generate fix（Copilot Autofix）**，审阅补丁与解释（注意：开发者对最终代码负全责，切勿盲目点接受）。
