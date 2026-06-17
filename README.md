# agent-workflow-init

A conservative initializer and health-check **skill** for agent-friendly workflow
workspaces — routing, logs, reviews, a DOM/operation memory, a lightweight knowledge
base, cleanup boundaries, and risk controls — for **Codex** and **Claude Code**.

> 中文说明见 [README.zh-CN.md](README.zh-CN.md)。

This is a **skill package, not a marketplace plugin.** You install it by copying the
folder into your agent's `skills/` directory (see below). There is no
`.codex-plugin/plugin.json`; nothing to "install" through a plugin marketplace.

## What it does

Two modes, pick the lightest that fits:

| Mode | Use when | Effect |
|---|---|---|
| `new` | You want a fresh, dedicated AI workflow folder | Generates a complete workspace skeleton. Creates the root `AGENTS.md` if missing; never overwrites. |
| `adapt` | A folder already has rules/workflows/logs and you want a health check | Writes a **read-only** health-check report under `Agent工作流助手/`. Touches nothing else. Only adds a lightweight improvement layer when you rerun with `--apply-light-upgrade` after approval. |

### What it never does

- Never overwrites or deletes your files (creates-if-missing only).
- Never moves or renames your existing entry docs, workflows, logs, or tools.
- In `adapt`, never modifies a mature existing system — it inspects, scores, and recommends.

## Language: it generates a Chinese workspace

By design there is **no `--language` flag**. The initializer always writes a Chinese
workspace; keeping two template trees in sync would be a large, fragile surface for
little gain. If you work in another language, your **agent localizes the generated
folder on request** — ordinary translation, no tooling. The post-`new` console output
reminds the agent to do this. See `SKILL.md` → "Localization".

## Install

Copy the `agent-workflow-init/` folder into your agent's skills directory:

- Codex (macOS/Linux): `~/.codex/skills/agent-workflow-init/`
- Codex (Windows): `C:\Users\<you>\.codex\skills\agent-workflow-init\`
- Claude Code (macOS/Linux): `~/.claude/skills/agent-workflow-init/`
- Claude Code (Windows): `C:\Users\<you>\.claude\skills\agent-workflow-init\`

Requires Python 3.9+. No third-party dependencies.

## Quick start

```bash
# new workspace
python3 scripts/init_agent_workflow.py --target ./demo --mode new

# health-check an existing folder (read-only)
python3 scripts/init_agent_workflow.py --target ./existing --mode adapt

# preview without writing anything
python3 scripts/init_agent_workflow.py --target ./demo --mode new --dry-run
```

On Windows use `python` (or `py`) instead of `python3`.

Useful flags: `--cleanup-cycle`, `--review-cycle` (both default `每周一次`),
`--apply-light-upgrade` (adapt only), `--dry-run`.

## Generated workspace (new mode)

```text
AGENTS.md            # constitution: startup order, folder map, cleanup boundary, risk floor
README.md            # daily routing shell
快速入口.md          # the one routing table (workflow + fluency level + read scope)
Agent执行手册.md     # execution discipline, new-task handling, scoring, web/batch rules
完整工作手册.md      # low-frequency system rules
系统设置/ 系统索引/ 资料库/ DOM地图/ 工作流/ 执行记录/ 巡查/
临时内容/ output/ 归档/ 工具/ _安装记录/ _待删除/
```

## Cleanup

`new` ships a cross-platform Python cleaner at
`工具/scripts/clear_pending_delete.py` — it works out of the box on macOS, Linux,
and Windows. The agent only schedules it (cron/launchd/Task Scheduler), or leaves it
manual.

Safety contract (any implementation): only clears `_待删除/` (keeping its `README.md`
and `_清理日志.txt`); refuses the workspace root, anything outside the workspace, and
`output/` / `归档/` / `执行记录/` / `巡查/`; supports `--dry-run`; logs every run.

## Verify

```bash
python3 scripts/init_agent_workflow.py --target ./demo --mode new --dry-run
python3 -m py_compile scripts/init_agent_workflow.py
python3 tests/test_template_manifest.py
python3 tests/test_initializer_behavior.py
```

## License

[MIT](LICENSE).
