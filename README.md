# Groove

> *Patina your workflow until it grooves.*

Turn a regular folder into a lightweight workflow OS for **Codex** and
**Claude Code**.

Groove creates the missing operating layer around recurring agent
work: routing, execution logs, review loops, DOM/operation memory, cleanup
boundaries, and risk controls. It is built for people whose agents handle
repeated work and should get faster over time instead of starting from zero in
every session.

> 中文说明见 [README.zh-CN.md](README.zh-CN.md)。

## Why this exists

Agent work often fails in the gap between "the model can do it" and "the next
agent knows how to do it again." This package gives that gap a small, durable
shape:

- **Agents stop starting from scratch.** Entry docs, routing tables, and workflow
  cards tell the next agent what to read and what to skip.
- **Real work turns into reusable process.** Execution logs and review loops
  compress repeated tasks into workflows.
- **Automation stays bounded.** Cleanup scripts, risk stops, and no-overwrite
  defaults keep workflow tooling from becoming dangerous.

This is **not** an automation platform, a task runner, or a giant agent
framework. It is a conservative workspace initializer and health-check **skill**.
Install once; let agents learn from real work.

## What it does

Two modes, pick the lightest that fits:

| Mode | Use when | Effect |
|---|---|---|
| `new` | You want a fresh, dedicated AI workflow folder | Generates a complete workspace skeleton. Creates the root `AGENTS.md` if missing; never overwrites. |
| `adapt` | A folder already has rules/workflows/logs and you want a health check | Prints a dialogue-first scoring handoff. Writes no report by default. Use `--write-health-report` only when you need an archival scaffold, and `--apply-light-upgrade` only after approval. |

### What it never does

- Never overwrites or deletes your files (creates-if-missing only).
- Never moves or renames your existing entry docs, workflows, logs, or tools.
- In `adapt`, never modifies a mature existing system — it inspects, scores, and recommends.

## Skill package, not a plugin

This is a **skill package, not a marketplace plugin.** You install it by copying the
folder into your agent's `skills/` directory (see below). There is no
`.codex-plugin/plugin.json`; nothing to "install" through a plugin marketplace.

## Language: it generates a Chinese workspace

By design there is **no `--language` flag**. The initializer always writes a Chinese
workspace; keeping two template trees in sync would be a large, fragile surface for
little gain. If you work in another language, your **agent localizes the generated
folder on request** — ordinary translation, no tooling. The post-`new` console output
reminds the agent to do this. See `SKILL.md` → "Localization".

## Install

Copy the `groove/` folder into your agent's skills directory:

- Codex (macOS/Linux): `~/.codex/skills/groove/`
- Codex (Windows): `C:\Users\<you>\.codex\skills\groove\`
- Claude Code (macOS/Linux): `~/.claude/skills/groove/`
- Claude Code (Windows): `C:\Users\<you>\.claude\skills\groove\`

Requires Python 3.9+. No third-party dependencies.

## Quick start

```bash
# new workspace
python3 scripts/init_agent_workflow.py --target ./demo --mode new

# health-check an existing folder (dialogue-first, no report by default)
python3 scripts/init_agent_workflow.py --target ./existing --mode adapt

# also write an archival health-check scaffold
python3 scripts/init_agent_workflow.py --target ./existing --mode adapt --write-health-report

# preview without writing anything
python3 scripts/init_agent_workflow.py --target ./demo --mode new --dry-run
```

On Windows use `python` (or `py`) instead of `python3`.

Useful flags: `--cleanup-cycle`, `--review-cycle` (both default `每周一次`),
`--write-health-report` (adapt only), `--apply-light-upgrade` (adapt only), `--dry-run`.

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
