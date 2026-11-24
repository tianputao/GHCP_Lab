# Track A · Vibe Coding 使用的典型模糊提示词

```text
帮我给订单 API 加一个部分退款接口 POST /orders/{order_id}/refunds，支持传入退款金额 amountCents，
扣减金额、更新订单状态，并加个 pytest 测试确保能跑通。
```

## 为什么这种开发方式极具迷惑性？

运行 Track A 自己的测试：
```bash
uv run pytest track_a_vibe_coding/tests/test_basic.py
```
你会发现 **Track A 自己的测试全绿通过！**

但只要运行企业级验收套件 `uv run python -m evaluator.compare`，立刻会暴露 Vibe Coding 在**无规格约束**下必然产生的 8 类经典缺陷：
1. **浮点金额漂移**：内部把分转成元做浮点减法，导致 IEEE-754 小数精度偏差（`1968.9999999999998`）。
2. **优惠券资损漏洞**：拿原价 `grossAmountCents` 而非实付 `paidAmountCents` 当可退上限。
3. **状态机缺失**：未支付或已取消订单也能被退款。
4. **重复提交双倍扣款**：缺少 `Idempotency-Key` 幂等与载荷冲突检查。
5. **高额退款绕过审批**：超过 500 元直接自动完成，缺少 `PENDING_APPROVAL` 与四眼审批。
6. **参数校验宽松**：缺少对负数、小数、原因、操作人的校验。
7. **审计日志空白**：没有 `GET /orders/{order_id}/audit-log` 留痕。
8. **架构漂移**：随意返回 `{ "msg": "..." }` 破坏了原项目 `{ "error": { "code", "message" } }` 错误信封。
