# mail-listener

> 把邮箱活动变成可持续运行、可自动化消费、可交给 Agent 的稳定事件流。

`mail-listener` 是一个面向开源与自动化场景的基础层项目，目标是把邮箱从“杂乱副通道”变成真正可用的事件入口。

它试图解决一个看似简单、实际很容易做烂的问题：

**如何让邮箱监听长期稳定运行、低延迟感知新邮件，并把这个信号干净地交给 Agent 或工作流，而不是从一堆脆弱脚本重新拼起？**

当前仓库已经内置了一个经过验证的 **Gmail IMAP IDLE 实现**，作为项目的**当前 adapter / 当前实现**。但项目定位本身并不是 Gmail-only，而是：

**一个面向未来多 provider 扩展的通用 mail listener 基础层。**

## 为什么会有这个项目

在真实系统里，邮箱仍是主要的 ingress channel 之一。

很多关键事件最早就是从邮箱出现的：

- 账号验证与安全通知
- 客户回复与共享邮箱动态
- 发票、回执、账单、告警
- 审批请求与平台通知
- 外部系统触发的工作流信号

问题在于，大多数团队处理邮箱监听的顺序都很糟：

- 先写临时脚本
- 再变成轮询任务
- 再变成一个脆弱的“临时守护进程”
- 最后变成谁都不想碰的 provider-specific 代码团

等到团队想把邮件接进 Agent 或自动化系统时，底座通常已经很脆了。

`mail-listener` 的价值，不是一次性包办所有业务逻辑，而是先把**邮件自动化的第一公里**做好：

> 稳定保持监听在线，快速感知新邮件，并输出一个其他系统可以信赖的标准化事件边界。

## 它解决的核心痛点

如果你受够了下面这些问题，`mail-listener` 就是为这种场景设计的：

- 轮询邮箱慢、吵、浪费资源
- 长连接监听一遇到重连、重启、secret、守护就变脆
- 脚本写死在某个 provider 上，没法复用
- Agent 系统虽然能“读邮件”，却没有一个稳定的 inbound event layer
- 邮箱接入逻辑和业务工作流混在一起，后面越来越难维护

## 典型使用场景

这个项目适合这些真实需求：

- 监听共享邮箱里的客户新回复
- 监听第三方平台发来的验证码或审批邮件
- 检测账单、回执、告警、通知等结构化邮件的到达
- 在邮箱变化时触发内部工作流
- 把邮件事件推给 Bot、任务系统、工作流引擎或 Agent
- 在笔记本、工作站、服务器、Agent 宿主机上长期运行邮箱监听器

## 它在 OpenClaw 场景里的位置

`mail-listener` 在 **OpenClaw / Agent 工作流** 里有一个比较清晰的位置。

很多 Agent 系统真正难的，不只是“收到信息后怎么推理”，而是：

**如何把邮箱里的变化稳定、持续、可自动化地送进系统。**

这正是 `mail-listener` 的位置。

在 OpenClaw 工作流里，它可以承担这层职责：

1. 长期保持邮箱监听在线
2. 低延迟感知新邮件事件
3. 把 provider 差异收敛成统一事件模型
4. 再把事件交给 OpenClaw 的 agent、skills、routing 或后续自动化流程

在 OpenClaw 里，它更适合这些场景：

- 收到新的运维邮件后触发 OpenClaw agent
- 把邮箱事件作为 skills 的输入
- 在进入真正业务逻辑前，先把邮件变化变成结构化信号
- 把 **mail ingress** 和 **reasoning / routing / action** 解耦

可以把这条边界理解成：

- `mail-listener` 负责：**mail ingress**
- OpenClaw 负责：**reasoning、routing、skills、action**

这个边界是故意设计出来的。

## 和 OpenClaw 定时任务（cron）的区别

`mail-listener` 和 OpenClaw 的 cron 解决的不是同一个问题。

### 适合用 `mail-listener` 的情况

- 触发条件是**邮箱发生变化**
- 希望用**事件驱动**，而不是定时轮询
- 希望新邮件到了以后尽快感知到
- 邮件本身就是触发源，后续 agent / workflow 在事件发生后再处理

### 适合用 OpenClaw cron 的情况

- 触发条件是**时间**而不是邮件
- 需要按固定周期执行任务
- 需要提醒、日报、定时检查、定期维护
- 即使没有新邮件，也希望任务按分钟 / 小时 / 天执行

### 常见组合方式

在 OpenClaw 场景里，这两者经常可以配合使用：

- `mail-listener` 负责发现新邮件
- OpenClaw agent / workflow 负责决定后续动作
- cron 负责补充后续的重试、汇总、提醒、超时处理或周期性维护

一个简单的判断方法是：

- **有新邮件到了** → 用 `mail-listener`
- **每天 9 点跑一次** → 用 OpenClaw cron

## 当前状态

当前仓库把经过验证的 **Gmail IMAP IDLE 监听实现** 收进来了，作为项目的**当前 adapter**。

今天已经具备：

- Gmail IMAP IDLE 监听器
- 适合 supervisor / launchd 托管的前台 daemon
- 自动重连 + 指数退避
- 滚动日志
- PID 锁文件，避免重复启动
- `--check` secret 自检
- 当前 adapter 对应的 `mail.message.received` 归一化事件结构
- 基础 CI 门禁（格式、lint、smoke tests）

当前还**没有**：

- OAuth 邮箱授权流
- 邮件正文解析
- 附件提取
- 下游业务编排
- Gmail 之外的成熟生产 adapter
- 完整 skills 实现

所以它现在已经是一个**可以独立运行的监听基础层**，但还不是一个“全套邮件自动化平台”。

## 适合谁

`mail-listener` 适合：

- 需要做邮箱驱动自动化的开发者
- 需要把邮件接进 Agent 工作流的团队
- 需要在 OpenClaw 中建立稳定 mail-ingress 层的使用者
- 希望监听器在真实环境里能长期跑住的运维/工程角色

## 不适合谁

如果你想要的是下面这些，那它当前还不是最合适的东西：

- 完整 helpdesk 产品
- 开箱即用的邮件全文解析平台
- all-in-one 工作流引擎
- 今天就成熟覆盖多 provider 的成品平台

这个项目当前的目标更基础，也更聚焦。

## 快速开始

```bash
cd mail-listener
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

先检查当前邮箱 secret 配置：

```bash
mail-listener --check
```

运行当前 Gmail IMAP IDLE 监听器：

```bash
mail-listener
```

详细日志模式：

```bash
mail-listener --verbose
```

## 仓库结构

```text
mail-listener/
├─ .github/workflows/ci.yml
├─ AGENTS.md
├─ LICENSE
├─ README.md
├─ README.zh-CN.md
├─ deploy/
├─ docs/
├─ examples/
├─ scripts/
├─ skills/
├─ src/
└─ tests/
```

关键设计点：

- `src/`：主项目源码，尽量保持 provider-neutral
- `adapters/`：放 provider 相关监听实现
- `events/`：定义下游系统消费的事件边界
- `skills/`：保留在顶层，方便未来拆分成独立 skill 仓库
- `AGENTS.md`：写给 coding agent 和维护者，不是写给最终用户的营销文案

## 质量门禁

本地与 CI 使用同一套门禁：

```bash
ruff format --check .
ruff check .
pytest
```

## 当前事件结构

当前 adapter 输出的归一化事件大致如下：

```json
{
  "event_type": "mail.message.received",
  "provider": "gmail-imap-idle",
  "mailbox": "listener@example.test",
  "exists_count": 42,
  "previous_exists_count": 41,
  "received_at": "2026-03-20T04:00:00+00:00"
}
```

## macOS 运行与托管

针对当前 Gmail IMAP IDLE 实现，仓库里已经带了：

- `scripts/gmail_idle_ctl.sh`：start / stop / status / logs
- `deploy/com.mail-listener.gmail-imap-idle.plist`：`launchd` 模板

示例：

```bash
./scripts/gmail_idle_ctl.sh check
./scripts/gmail_idle_ctl.sh start
./scripts/gmail_idle_ctl.sh status
./scripts/gmail_idle_ctl.sh logs
```

## 后续演进方向

这个项目的长期方向不是“只做 Gmail”，而是：

- 一个可复用的 mail-listener core
- 多个 provider adapter
- 稳定的 mail-event contract
- 上层可选的 skills / workflow / automation 包

Gmail IMAP IDLE 只是这个方向上第一个已经验证过的 adapter。

## 许可证

Apache License 2.0。
