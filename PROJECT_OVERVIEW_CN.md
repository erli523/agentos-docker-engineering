# AgentOS Docker 工程实践说明

> 本仓库是基于 [agno-agi/agentos-docker](https://github.com/agno-agi/agentos-docker) 的学习与二次开发分支，保留上游 Apache-2.0 许可证和提交历史。本文明确区分上游能力与本次工程改动。

## 项目定位

AgentOS Docker 是一个面向生产形态的 Agent 后端模板。它把代码 Agent、Team、Workflow 和运行时创建的组件注册到统一服务，通过 REST、SSE、MCP 和聊天接口对外提供能力，并把 session、run、知识、Trace、评测和调度信息保存到 PostgreSQL。

本次实践重点是 Agent 后端的配置可移植性、工具执行、用户隔离、状态持久化和可靠性边界。核心问题不是“Agent 能不能回答”，而是服务重启、认证、多用户、HITL、Tracing 和长任务中断时系统实际会怎样。

## 核心技术栈

| 层次 | 技术与用途 |
|---|---|
| Agent 运行时 | Python 3.14、Agno 3.0.4、AgentOS、Agent/Team/Workflow |
| 接口 | FastAPI、REST、SSE、MCP、Slack 等可选 Interface |
| 模型与工具 | OpenAI-compatible Chat/Embedding、Function Calling、文件/计算/搜索工具、HITL |
| 数据层 | PostgreSQL、pgvector、Knowledge、session/run、组件版本、Trace、Eval、Scheduler |
| 安全 | JWT/JWKS、scope 权限、以 token subject 为准的用户隔离 |
| 工程化 | Docker Compose、Ruff、Mypy、pytest、smoke eval、健康检查 |

## 核心思路

```text
REST / SSE / MCP / Interface
  → AgentOS 统一运行时
  → Code Agents / Team / Workflow / Studio Components
  → Model + Tools + Knowledge
  → PostgreSQL + pgvector
  → sessions / runs / traces / evals / schedules
```

代码组件适合版本控制，Studio 组件适合运行时创建和发布；二者共享数据库和服务入口。Team 负责成员委派与共享上下文，Workflow 负责确定性步骤编排。JWT 中间件把外部身份映射到用户级 session 和 memory，MCP 则把 AgentOS 能力暴露给 Claude、ChatGPT 等客户端。

## 本次自主改进

1. **可移植模型与 Embedding**：把 chat、embedding 和 Eval Judge 从隐式 OpenAI 绑定改成独立的兼容端点配置，真实跑通 DeepSeek Chat、Function Calling 和阿里 1024 维 Embedding。
2. **可选远程依赖降级**：为 Agno Docs MCP 和 Web Search 增加显式开关，受限网络下不再因远程 DNS 故障导致整个 API lifespan 退出。
3. **Windows/Docker 启动可靠性**：用 `.gitattributes` 和镜像构建防御处理 shell 脚本 CRLF，并增加回归测试。
4. **评测契约修复**：收紧简单记忆请求的回答规则，使工具可靠性和 Judge 同时通过；评测 Judge 与运行 provider 保持一致。

## 验证结果

- Unit tests **8/8**；Ruff format、Ruff check、Mypy 全部通过；上游 smoke eval 从基线 0/6 恢复到 **6/6**。
- 真实执行代码 Agent 文件工具、Team 成员委派、Studio Agent/Team/Workflow 发布和知识库有依据回答。
- SSE 样本收到 96 个事件，覆盖 RunStarted、Model、Tool、Content、RunCompleted。
- MCP 握手发现 9 个工具，并完成 deployment-check 与 HITL pause/continue/restore。
- JWT 验证覆盖无 token、坏签名、缺 scope、双用户 session 隔离和私有记忆隔离。
- 最终镜像重建后，组件、知识、完成态 run、session、调度和 Trace 均可读取。

## 适合作为项目经历的价值

这个项目展示了 Agent 服务化、Function Calling、MCP、SSE、JWT、多用户隔离、PostgreSQL/pgvector、Tracing、Eval 和调度。它还能体现对可靠性边界的判断：数据库中有运行记录，不等于后台执行具备断点续跑能力。

## 已知边界

- 当前模板没有 durable queue 和独立 worker。API 进程在任务执行中退出后，数据库可能留下 `RUNNING` 记录，但不会自动恢复执行。
- `/resume` 用于 SSE 重连，不等同于重启任务；孤儿运行的 continue 在 Agno 3.0.4 中仍存在上游反序列化问题。
- Cancel 是协作式取消，正在进行的长模型或工具调用不能被立即强制终止。

## 上游与许可证

- 上游仓库：<https://github.com/agno-agi/agentos-docker>
- AgentOS 文档：<https://docs.agno.com/agent-os>
- 许可证：Apache License 2.0
