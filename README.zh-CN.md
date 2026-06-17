# agent-workflow-init

把一个普通文件夹变成 **Codex** 和 **Claude Code** 都能使用的轻量工作流系统。

Agent Workflow Init 给重复性 agent 工作补上一层缺失的操作系统:入口路由、执行日志、巡查复盘、DOM/操作记忆、清理边界和风险确认。它适合那些已经开始让 agent 做固定工作的人:下一次 agent 进来时,不应该每次都从零摸索,而应该沿着真实任务越跑越顺。

> English: see [README.md](README.md).

## 为什么需要它

agent 的问题经常不在"模型能不能做",而在"下一个 agent 能不能照着做、越做越快"。这个包给这件事一个小而稳的结构:

- **不再每次从零开始。** 入口文档、快速路由和工作流卡片告诉下个 agent 该读什么、不该读什么。
- **真实任务会沉淀成流程。** 执行记录和巡查复盘把重复任务压缩成可复用工作流。
- **自动化有边界。** 清理脚本、风险停点和不覆盖默认值,让工作流工具不会变危险。

它不是自动化平台,不是任务调度器,也不是大而全 agent 框架。它是一个保守的「初始化 + 体检」**技能(skill)**。安装一次,让 agent 从真实任务里学习。

## 它做什么

两种模式,选最轻的那个:

| 模式 | 什么时候用 | 效果 |
|---|---|---|
| `new` | 想要一个全新的专用 AI 工作流文件夹 | 生成完整工作区骨架。根 `AGENTS.md` 缺失才建,绝不覆盖。 |
| `adapt` | 文件夹已有规则/工作流/日志,想做体检 | 在 `Agent工作流助手/` 下写一份**只读**体检报告,不动其他任何文件。仅在你确认后用 `--apply-light-upgrade` 再跑,才加一层轻量改进。 |

### 它绝不做的事

- 绝不覆盖或删除你的文件(只"缺了才建")。
- 绝不移动或重命名你现有的入口文档、工作流、日志、工具。
- `adapt` 绝不改动成熟系统——只体检、打分、给建议。

## 它是 skill 包,不是 plugin

这是一个 **skill 包,不是插件市场的 plugin**。安装方式是把文件夹复制到 agent 的 `skills/`
目录(见下),没有 `.codex-plugin/plugin.json`,不需要通过插件市场安装。

## 语言:它生成中文工作区

**刻意不做 `--language` 开关**。初始化器始终生成中文工作区——维护中英两套模板同步是个又大又
脆的负担,收益却不大。如果你的工作语言不是中文,**由你的 agent 按需把生成的文件夹本地化**——
就是普通翻译,不需要工具。`new` 跑完控制台会提示 agent 做这步。详见 `SKILL.md` →「Localization」。

## 安装

把 `agent-workflow-init/` 文件夹复制到 agent 的 skills 目录:

- Codex (macOS/Linux): `~/.codex/skills/agent-workflow-init/`
- Codex (Windows): `C:\Users\<你>\.codex\skills\agent-workflow-init\`
- Claude Code (macOS/Linux): `~/.claude/skills/agent-workflow-init/`
- Claude Code (Windows): `C:\Users\<你>\.claude\skills\agent-workflow-init\`

需要 Python 3.9+,无第三方依赖。

## 快速开始

```bash
# 新工作区
python3 scripts/init_agent_workflow.py --target ./demo --mode new

# 体检已有文件夹(只读)
python3 scripts/init_agent_workflow.py --target ./existing --mode adapt

# 只预览,不写任何文件
python3 scripts/init_agent_workflow.py --target ./demo --mode new --dry-run
```

Windows 上把 `python3` 换成 `python`(或 `py`)。

常用参数:`--cleanup-cycle`、`--review-cycle`(默认都是 `每周一次`)、
`--apply-light-upgrade`(仅 adapt)、`--dry-run`。

## 清理

`new` 会预置一份跨平台 Python 清理器 `工具/scripts/clear_pending_delete.py`——
macOS / Linux / Windows 开箱即用。agent 只需挂定时任务(cron/launchd/计划任务),或保持手动。

安全约束(任何实现都一致):只清空 `_待删除/`(保留其 `README.md` 和 `_清理日志.txt`);
拒绝工作区根、区外路径,以及 `output/` / `归档/` / `执行记录/` / `巡查/`;支持 `--dry-run`;
每次运行写日志。

## 验证

```bash
python3 scripts/init_agent_workflow.py --target ./demo --mode new --dry-run
python3 -m py_compile scripts/init_agent_workflow.py
python3 tests/test_template_manifest.py
python3 tests/test_initializer_behavior.py
```

## 许可

[MIT](LICENSE)。
