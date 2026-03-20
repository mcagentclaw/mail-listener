# mail-ingress-kit

一个面向 **邮件接入（mail ingress）**、**邮箱监听（mailbox listening）**、**邮件事件分发（mail event delivery）** 的基础骨架项目。

这个仓库**刻意不定位为 Gmail-only**。它的目标是为后续支持多种邮箱提供商、多种接入方式预留清晰边界，同时兼顾 **human users** 与 **agent users**，并默认兼容 **OpenClaw / Codex / Cloud Code** 这类 agent 工作流。

## 项目价值

很多自动化系统都需要一层稳定的邮件接入能力，用来：

- 监听一个或多个邮箱
- 将收到的邮件归一化为统一事件
- 把事件投递给下游技能、Agent 或业务流程
- 把提供商差异收敛在 adapter 层，而不是扩散到整个项目

本次先完成基础骨架，不做重型实现迁移。

## 当前定位

- **项目类型：** 基础骨架 / foundation
- **核心关注：** mailbox listener + mail ingress event pipeline
- **设计风格：** skill-first、adapter-oriented、agent-compatible
- **当前已验证实现备注：** Gmail 的 IMAP IDLE 已被验证为一个可行的首个 adapter 方向，但这里只把它视为当前实现说明，而不是产品名称或整体定位

## 目录结构

```text
mail-ingress-kit/
├─ AGENTS.md
├─ LICENSE
├─ README.md
├─ README.zh-CN.md
├─ pyproject.toml
├─ .gitignore
├─ docs/
│  └─ architecture.md
├─ examples/
│  └─ sample-event.json
├─ scripts/
│  └─ bootstrap.sh
├─ skills/
│  └─ README.md
└─ src/
   └─ mail_ingress_kit/
      ├─ __init__.py
      ├─ adapters/
      │  └─ __init__.py
      ├─ core/
      │  └─ __init__.py
      ├─ events/
      │  └─ __init__.py
      └─ skills/
         └─ __init__.py
```

## 开发建议

推荐遵循“源码与运行环境分离”的方式：

- 源码放在仓库内
- 运行环境使用本地虚拟环境或外部部署环境
- `.venv/`、缓存、构建产物、密钥文件不纳入版本控制

示例：

```bash
cd mail-ingress-kit
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 近期路线图

- 定义统一的邮件事件模型
- 明确 adapter 接口与生命周期
- 把 Gmail IMAP IDLE 作为首个已验证 adapter 的 implementation note 写清楚
- 设计 skills 的独立发布边界
- 后续再补测试、CI、示例集成

## 候选仓库名

- `mail-ingress-kit`
- `mail-event-bridge`
- `mailbox-ingress`
- `mail-listener-core`
- `mail-adapter-kit`

## 许可证

Apache License 2.0。
