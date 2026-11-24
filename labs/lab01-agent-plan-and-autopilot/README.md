# Lab 01 · Plan Mode、Agent / Autopilot、Auto 路由与 Cloud Agent 委派

> **对应高级能力**：Plan → 人工审批 → Agent/Autopilot 自主闭环、Task-Aware Auto 模型路由、多文件错误自愈、现代 Copilot CLI、GitHub Issue → Copilot Cloud Agent 云端异步交付。  
> **预计时长**：25–35 分钟  
> **建议打开方式**：用 VS Code 单独打开本目录 `labs/lab01-agent-plan-and-autopilot/`（或在根目录打开并用 `#file` 精准指定路径）。

---

## 0. 启动前验证基线

在终端进入本目录并验证环境：

```bash
cd labs/lab01-agent-plan-and-autopilot
npm install      # 若已在根目录跑过 npm run install:all 可跳过
npm run verify   # 运行 tsc --noEmit + node:test 基线测试
```

预期结果：3 个基线测试全部通过（默认内置 25 条确定性种子任务）。

---

## 练习 1：Plan Mode → 人工审批 → Agent / Autopilot 实现游标分页

### 为什么要先 Plan 再执行？
直接让 Agent 开写容易忽略边界（排序稳定性、非法参数返回码、向后兼容性）。2026 年推荐的标准节奏是：**先 Plan 审阅方案 → 再切换到 Interactive/Agent 或 Autopilot 执行 → 最后由人审查 Diff 和测试**。

### 操作步骤
1. 打开 VS Code Copilot Chat，在底部 **Session Target** 优先选择 **Copilot**（Agent Host 模式；若你的环境仍为旧 Local，请参考根目录 `COMPATIBILITY-2026.md`）。
2. 模型选择器先保持 **Auto**（Task-Aware Auto，观察它在规划与实现阶段自动选用的模型）。
3. 将模式切换到 **Plan**，粘贴以下需求：

```text
请先只读分析 #file:src/routes/tasks.ts、#file:src/store.ts、#file:src/types.ts 和 #file:tests/tasks.test.ts，
给出为 GET /tasks 增加游标分页（cursor-based pagination）的详细实施计划，先不要修改代码。

需求与验收标准：
1. 查询参数：limit（整数，默认 10，最小 1，最大 50）和可选 cursor（base64 编码的 task id）。
2. 排序规则：按 createdAt 降序，时间相同按 id 降序保证稳定分页。
3. 响应结构：{ data: Task[], nextCursor: string | null, hasMore: boolean }。
4. 非法 limit（非整数、<=0、>50）或无效/不存在的 cursor 返回 HTTP 400，使用项目现有错误格式 { error: { code, message } }。
5. 不破坏现有 POST / PATCH / DELETE / GET /:id 接口。
6. 更新并补充 tests/tasks.test.ts，覆盖第 1 页、第 2 页、末页、非法参数和空结果。
```

4. **人工审核计划**：检查计划是否明确覆盖了“末页 `nextCursor: null, hasMore: false`”以及“非法 cursor 返回 400”。如有遗漏，先在 Plan 模式补充要求。
5. **进入执行**：
   - **受控演示**：点击 Plan 下方的 **Start Implementation**（或切回 **Interactive / Agent**），逐项观察它编辑多文件并运行 `npm run verify`。
   - **自主执行体验（Autopilot）**：在隔离分支中切到 **Autopilot**（Copilot Agent Host 下位于模式选择器；旧 Extension Host 下位于权限选择器），观察它自动改代码 → 跑测试 → 根据报错自修 → 直到验收通过。
6. **人工验收**：
   ```bash
   git diff
   npm run verify
   ```

---

## 练习 2：观察 Agent 错误自愈循环（限流中间件）

测试 Agent 在遇到编译错误或测试失败时的 `Plan → Code → Test → Iterate` 闭环：

```text
在 #file:src/app.ts 中增加一个内存滑动窗口限流中间件，并写独立单元测试验证：
- 每个来源 IP 每分钟最多 60 次请求（可通过 createApp 参数配置上限，方便测试）
- 返回标准响应头：X-RateLimit-Limit、X-RateLimit-Remaining、X-RateLimit-Reset
- 超限时返回 429 Too Many Requests，响应体遵循 { error: { code: "RATE_LIMITED", message } } 并带 Retry-After 头
- /health 探针不受限流影响
- 完成后运行 npm run verify 确保 TypeScript 严格模式和全部测试通过
```

观察点：记录 Agent 一共经历了多少次“运行测试 → 读取报错 → 修复 → 重跑”。

---

## 练习 3：现代 Copilot CLI 终端工作流（可选，需本机已安装 `copilot` CLI）

> 2026 年统一使用独立 `copilot` 命令，不再使用旧版 `gh copilot suggest/explain` 扩展写法。

```bash
# 启动交互式终端助手
copilot

# 常用交互模式（在 copilot 会话内）
@src/routes/tasks.ts 解释当前路由校验有哪些重复逻辑
/plan 为 GET /tasks 增加按 status 和 priority 过滤的能力，暂不改文件
# 按 Shift+Tab 切换 standard / plan / autopilot 模式

# 或非交互受限续跑演示（仅在隔离分支运行）
copilot --autopilot --max-autopilot-continues 5 -p "运行 npm run verify 并总结当前测试覆盖缺口，不修改代码"
```

---

## 练习 4：GitHub Issue → Copilot Cloud Agent 云端异步交付

本仓库已推送到 `https://github.com/tianputao/GHCP_Lab`，并预先准备好了 Issue 模板与 GitHub Actions CI（`.github/workflows/ci.yml`）：

1. 打开仓库的 **Issues → New issue**，选择 **Cloud Agent Task (Lab 01)** 模板提交 Issue。
2. 在 Issue 右侧 **Assignees** 选择 **Copilot**（需要付费 Copilot 计划并启用 Cloud Agent 策略）。
   - 或在本地终端使用 GitHub CLI 触发：
     ```bash
     gh issue edit <ISSUE_NUMBER> --repo tianputao/GHCP_Lab --add-assignee "@copilot"
     ```
3. 观察 Cloud Agent 自动创建分支、编写代码、运行测试并创建 Draft PR。
4. 打开 PR 检查 GitHub Actions CI 结果，评论 `@copilot` 提出一轮修改意见，体验异步迭代与人工 Merge 门禁。

---

## 完成后清理现场（便于重复演示）

```bash
git checkout -- labs/lab01-agent-plan-and-autopilot/
git clean -fd labs/lab01-agent-plan-and-autopilot/
npm run verify
```
