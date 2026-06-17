---
name: groove
description: Set up or adapt an Agent Workflow OS workspace. Use when the user asks to create a new agent workflow workspace, install/initialize a workflow assistant, compare an existing workflow system against Agent Workflow OS, generate an adapt/health-check report for existing workflows, or after user approval lightly add an improvement layer such as a candidate-workflow rule, DOM map template, lightweight knowledge base, and a `_待删除/` recycle area with a cleanup script.
---

# Groove

This skill initializes or adapts an Agent Workflow OS workspace. It is an install/adaptation skill, not a daily business-execution skill.

It works the same for **codex and Claude Code** — the SKILL.md frontmatter (`name` + `description`) and the bundled `scripts/`/`references/`/`templates/` are agent-neutral. The only agent-specific file is `agents/openai.yaml` (codex interface metadata), which other agents simply ignore.

It is also **OS-neutral**. The Python initializer produces a pure-markdown workspace that runs identically on macOS, Linux, and Windows. It also ships a cross-platform Python cleanup script (`工具/scripts/clear_pending_delete.py`) by default, so cleanup works out of the box; the agent only schedules it per-OS (see "Cleanup script" below). Localization is the one piece left to the agent: the script always writes Chinese, and the agent rewrites the workspace into another language on request (see "Localization").

Core rule: install once, then leave runtime work to the target folder's short entry chain: `AGENTS.md` -> `README.md` -> matched workflow by A/B/C/D fluency level. Keep `Agent执行手册.md` and `完整工作手册.md` for exceptions, new tasks, review, maintenance, or unclear routing. Do not add installation instructions to the agent's daily preflight path.

For workflow-training changes, use `references/workflow-training-sources.md` as the evidence note. Do not turn it into a default runtime document; only absorb ideas that become concrete triggers, actions, readbacks, risk stops, or review compression.

`templates/` is the single source of truth for what gets generated. The Python script owns the layout, the file manifest, and the small amount of dynamic text (health report, init report); the actual file **contents** live as plain markdown under `templates/`, mirroring the generated workspace. The manifest invariant is tested: every path in `NEW_FILES` / `LIGHT_UPGRADE_FILES` must exist under `templates/`, and vice versa.

## Mode Decision

Two modes only. Use the lightest one that fits the target:

| Mode | Use when | Root `AGENTS.md` |
|---|---|---|
| `new` | The user wants a new dedicated AI workflow folder (empty or fresh) | Create if missing; never overwrite |
| `adapt` | The project already has rules/workflows/logs and the user wants a health check | Do not touch |

If the user does not specify a mode, choose `new` for an empty or dedicated new folder. Choose `adapt` when you see existing workflow surfaces such as `AGENTS.md`, `README.md`, `快速入口.md`, `工作流/`, `执行记录/`, `执行日志/`, DOM maps, or similar self-maintenance structure.

`adapt` is read-only by default: it writes a health-check report under `Agent工作流助手/` and never modifies the user's existing files. It only adds a lightweight improvement layer when the user approves and you rerun with `--apply-light-upgrade`.

## What To Ask

Do not ask what work the user does, what tasks repeat, or which files should be saved. Those are learned from later execution.

**Before running `new`, always ask these three — do not silently accept the defaults, and ask BEFORE running so the answers go in as flags (asking after generation is too late: the values are already written and not overwritten):**

- **language** — the workspace generates in **Chinese by default**. Ask what language the user works in. If it is not Chinese, run first, then rewrite the generated folder into that language (see "Localization"). There is no flag for this — it is your post-generation step.
- **cleanup cycle** for `_待删除/` — ask their preference; default `每周一次`. Pass via `--cleanup-cycle`.
- **review cycle** for workflow 巡查 — ask their preference; default `每周一次`. Pass via `--review-cycle`.

Ask these only when relevant:

- **target folder** if not clear;
- **mode** if both `new` and `adapt` are plausible and the choice affects existing files;
- in `adapt`, **whether to apply the light upgrade** after the user reads the report; default is no.

If the user explicitly says "just use defaults", skip the three and run with defaults — but offer them once, do not assume silently.

## Run The Initializer

The script lives next to this file. From the skill folder:

```bash
python3 scripts/init_agent_workflow.py --target <folder> --mode <new|adapt>
```

On Windows, `python3` is often not on PATH — use `python` (or `py`) instead. Use the absolute path if you are not running from inside the skill folder. Install location depends on the agent and OS:

- codex (macOS/Linux): `~/.codex/skills/groove/`
- codex (Windows): `C:\Users\<you>\.codex\skills\groove\`
- Claude Code (macOS/Linux): `~/.claude/skills/groove/`
- Claude Code (Windows): `C:\Users\<you>\.claude\skills\groove\`

```bash
python3 ~/.codex/skills/groove/scripts/init_agent_workflow.py --target <folder> --mode <new|adapt>
```

Useful options:

```bash
--cleanup-cycle "每周一次"      # _待删除/ 自动清理周期
--review-cycle "每周一次"       # 工作流巡查周期
--apply-light-upgrade           # adapt only, after user approval
--dry-run                       # print intended actions, write nothing
```

The script is conservative:

- creates missing files and directories;
- skips existing files (never overwrites);
- never moves or deletes user files;
- writes an initialization report to `_安装记录/`;
- in `adapt`, only writes a health-check report by default;
- in `adapt --apply-light-upgrade`, adds lightweight improvement files after user approval, skipping existing files.

## Localization (agent does this, on request)

The script always writes Chinese **by design** — there is no `--language` flag and no multi-language template machinery, because keeping two template trees in sync is a large, fragile surface for little gain. Language is the agent's job, not the script's.

So if the user's working language is not Chinese:

1. Run the initializer normally (it generates the Chinese workspace).
2. Then **you (the agent) rewrite the generated files in the user's language**, file by file, preserving structure and the entry chain. This is ordinary translation work — no tooling needed.
3. **Keep directory names in Chinese** (recommended): the cleanup script's protected-dir list, the cross-references between docs, and `工具/scripts/clear_pending_delete.py` all match Chinese folder names. Translate only the **file contents**. If the user explicitly wants translated directory names too, you must also update every hardcoded path and the cleanup script to match.

The post-`new` console output reminds you of this step, so it is not silently skipped.

## Cleanup script (shipped by default; agent only schedules it)

`new` now **ships a cross-platform Python cleaner** at `工具/scripts/clear_pending_delete.py` so cleanup works out of the box. It runs identically on macOS, Linux, and Windows with no BOM/encoding pitfalls. The agent's only remaining job is to **schedule** it on the chosen cycle (or leave it manual):

- **Schedule it**: `cron`/`launchd` on macOS/Linux, Task Scheduler on Windows, pointing at the local Python + the script's absolute path.
- **Or leave it manual**: tell the user the disposable files live in `临时内容/` and `_待删除/`; they can delete by hand. `output/`/`归档/`/`执行记录/`/`巡查/` are never touched.

Always verify with `python 工具/scripts/clear_pending_delete.py --dry-run` first.

If the user specifically wants a PowerShell `.ps1` (must be **UTF-8 with BOM**, PS 5.1-compatible syntax only — no `?.`, no ternary `?:`) or a `.sh` instead of the Python default, swap in the known-good template from `references/cleanup-scripts.md`.

Whatever the implementation, the contract is fixed: only clears `_待删除/` (keeping its `README.md` and `_清理日志.txt`); refuses the workspace root, anything outside the workspace, and `output/`/`归档/`/`执行记录/`/`巡查/`; supports a dry-run; appends `time / mode / count` to `_待删除/_清理日志.txt` on every run.

## Expected Results

`new` mode creates the streamlined workspace:

```text
AGENTS.md            # 宪法：启动顺序/文件夹地图/归类默认/清理边界/风险底线/命名规则
README.md            # 日常分流路由壳（约 10 行）
快速入口.md          # 唯一路由表（工作流 + 流畅等级 + 读取范围）
Agent执行手册.md     # 执行纪律、新任务、评分、网页/批量规则
完整工作手册.md      # 低频系统规则
系统设置/            # 节奏设置、风险动作默认规则
系统索引/            # 工作区地图、工作流总览、产出归类与命名规范、用户纠正处理规则、术语表
资料库/              # 固定规则、业务背景、网站入口（常用链接地图）、账号与权限说明
DOM地图/             # _DOM地图模板
工作流/              # _工作流模板、_候选流程规则、_examples模板（空工作区，无预置示例）
执行记录/原始记录/   # _执行记录模板（原始记录目录为空，真实任务后写入）
巡查/                # 巡查执行流程、_巡查日志模板、滚动未决（跨巡查常驻的未决项台账，不丢不回链）；巡查日志/（按日期滚动，最新一份即当前结论，含改动方案+执行统计，对话框确认；旧份长期保留）
临时内容/            # 草稿/中间文件/验证文件（可清理）
output/              # 正式产出/可复用样例/验证证据（永久保留）
归档/                # 旧工作流/旧日志/旧产出
工具/                # README + scripts/（默认预置跨平台 clear_pending_delete.py）+ checkers/connectors/snippets
_安装记录/           # 安装记录 + 初始化报告
_待删除/             # 显眼回收区（脚本自动清）
```

Runtime entry roles:

- `AGENTS.md`: hard entry / constitution. Startup order, folder map, classification defaults, cleanup boundary, risk floor, naming rule.
- `README.md`: the daily routing shell. Points at `快速入口.md` and the A/B/C/D fluency table.
- `快速入口.md`: the only routing table (workflow + fluency level + read scope).
- `Agent执行手册.md`: execution discipline, scoring triggers, new-task handling, closeout checks, web/batch rules.
- `完整工作手册.md`: low-frequency system principles, read only for maintenance, review, or unclear routing.
- `临时内容/`, `output/`, `归档/`, `_待删除/`: lifecycle directories. Agent output defaults to `临时内容/`; confirmed/delivered output goes to `output/`; the agent never deletes — discarded content moves to `_待删除/` for the cleanup script; `output/`, `归档/`, `执行记录/`, `巡查/` are never auto-cleaned (the rolling 巡查日志 is the distilled change-history kept after raw logs are pruned).

`adapt` mode creates `Agent工作流助手/现有工作流体检报告.md` as a **half-finished scaffold**. The Python script cannot do a semantic health check — it only gathers evidence (a recursive structure scan + a list of entry docs) and lays out an empty capability-comparison table. **You (the agent) must then read the actual entry docs (`README`/`AGENTS.md`/`agent.md`/`CLAUDE.md` and whatever the scan surfaced) and fill the table by semantic comparison**, scoring each Agent-Workflow-OS capability **0–3** per the rubric the report carries (0 缺 / 1 雏形 / 2 成文可用 / 3 成熟或更强 / — 不适用), then computing the total and a maturity band — that is the "score" of the inspected system. Do NOT trust filename matching: a capability implemented under a different name, or implemented more strongly (e.g. an existing scheduled cleanup script), scores 2–3 — never score it 0 or suggest "upgrading" it. Only rows you score 0 become gaps, and only those drive suggestions. It does not modify existing workflows by default.

When the user approves the suggested changes, rerun adapt with:

```bash
python3 scripts/init_agent_workflow.py --target <folder> --mode adapt --apply-light-upgrade
```

This adds a lightweight layer (candidate-workflow rule, knowledge base basics, DOM map template, `_待删除/` recycle area) under `Agent工作流助手/`, skipping existing files. It does not replace the project's current entry chain, workflow docs, DOM maps, logs, or tools.

## Verification

After initialization, run at least:

```bash
python3 scripts/init_agent_workflow.py --target <folder> --mode <mode> --dry-run
python3 -m py_compile scripts/init_agent_workflow.py
```

For skill development, validate the skill folder with the system skill validator when available (codex example; adjust the path to your install location):

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/groove
```

## Red Lines

- Do not overwrite user workflow files.
- Do not move or delete user content.
- Do not make installation docs part of daily runtime reading.
- Do not make `完整工作手册.md` part of the default context for ordinary tasks.
- If you swap the default Python cleaner for a Windows PowerShell one, save it UTF-8 **with BOM** and avoid PS7-only syntax; the cleanup script (any OS) must never touch `output/`, `归档/`, `执行记录/`, `巡查/`.
- In `adapt`, do not treat a mature existing system as something to migrate; inspect, compare, recommend, and supplement only after user approval.
