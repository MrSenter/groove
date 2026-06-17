#!/usr/bin/env python3
"""Initialize or adapt an Agent Workflow OS workspace.

Modes:
- new   : create the streamlined Agent Workflow OS workspace (templates/ is
          the single source of truth for its contents and layout).
- adapt : inspect an existing workflow folder, write a health-check report,
          and only with --apply-light-upgrade add a lightweight improvement
          layer. Never overwrites existing user files.

This script is intentionally conservative:
- create missing files and directories;
- skip existing files by default;
- never move or delete user files.

File contents live as plain markdown under `../templates/`, mirroring the
generated workspace layout. This script only owns the layout, the manifest,
and the small amount of dynamic text (health report, init report). Edit a
generated file's wording by editing its template, not this script.

Localization: this script always writes Chinese. There is no language flag by
design — to produce another language, generate the workspace first, then the
agent rewrites the generated folder in the target language (see SKILL.md).
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


APP_NAME = "Agent Workflow OS"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@dataclass
class ActionLog:
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_created(self, path: Path) -> None:
        self.created.append(str(path))

    def add_skipped(self, path: Path) -> None:
        self.skipped.append(str(path))

    def add_updated(self, path: Path) -> None:
        self.updated.append(str(path))

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def file_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def ensure_dir(path: Path, log: ActionLog, dry_run: bool) -> None:
    if path.exists():
        return
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)
    log.add_created(path)


def safe_write(path: Path, content: str, log: ActionLog, dry_run: bool, *, bom: bool = False) -> None:
    """Create a file only if it does not already exist.

    bom=True writes UTF-8 with a BOM (utf-8-sig). The cleanup .ps1 MUST be
    written this way so Windows PowerShell 5.1 reads the Chinese content as
    UTF-8 instead of mis-decoding it as ANSI.
    """
    if path.exists():
        log.add_skipped(path)
        return
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8-sig" if bom else "utf-8"
        path.write_text(content.rstrip() + "\n", encoding=encoding)
    log.add_created(path)


def md_list(items: Iterable[str]) -> str:
    values = list(items)
    if not values:
        return "- 无"
    return "\n".join(f"- `{item}`" for item in values)


def render(rel_path: str, **subs: str) -> str:
    """Read templates/<rel_path> and substitute only known {{key}} tokens.

    User-facing placeholders like {{系统名}} or {{任务名称}} are left intact —
    only the keys passed in `subs` are replaced, so static templates are
    returned verbatim.
    """
    text = (TEMPLATES_DIR / rel_path).read_text(encoding="utf-8")
    for key, value in subs.items():
        text = text.replace("{{" + key + "}}", value)
    return text


# ---------------------------------------------------------------------------
# new 模式：目录布局（含空目录；与 templates/ 镜像一致）
# ---------------------------------------------------------------------------

def standard_layout(base: Path) -> list[Path]:
    return [
        base / "系统设置",
        base / "系统索引",
        base / "资料库",
        base / "DOM地图",
        base / "工作流",
        base / "执行记录" / "原始记录",
        base / "巡查" / "巡查日志",
        base / "临时内容" / "草稿",
        base / "临时内容" / "中间文件",
        base / "临时内容" / "验证文件",
        base / "output" / "正式产出",
        base / "output" / "可复用样例",
        base / "output" / "验证证据",
        base / "归档" / "旧工作流",
        base / "归档" / "旧日志",
        base / "归档" / "旧产出",
        base / "工具" / "checkers",
        base / "工具" / "connectors",
        base / "工具" / "scripts",
        base / "工具" / "snippets",
        base / "_安装记录",
        base / "_待删除",
    ]


# new 模式生成的全部文件（相对路径 = 对应模板路径）。
# 顺序决定初始化报告里 Created 列表的可读顺序。
NEW_FILES = [
    "README.md",
    "AGENTS.md",
    "快速入口.md",
    "Agent执行手册.md",
    "完整工作手册.md",
    "系统设置/节奏设置.md",
    "系统设置/风险动作默认规则.md",
    "系统索引/工作区地图.md",
    "系统索引/工作流总览.md",
    "系统索引/产出归类与命名规范.md",
    "系统索引/用户纠正处理规则.md",
    "系统索引/术语表.md",
    "资料库/README.md",
    "资料库/固定规则.md",
    "资料库/业务背景.md",
    "资料库/网站入口.md",
    "资料库/账号与权限说明.md",
    "DOM地图/_DOM地图模板.md",
    "工作流/_工作流模板.md",
    "工作流/_候选流程规则.md",
    "工作流/_examples模板.md",
    "执行记录/_执行记录模板.md",
    "巡查/巡查执行流程.md",
    "巡查/_巡查日志模板.md",
    "巡查/滚动未决.md",
    "临时内容/README.md",
    "output/README.md",
    "工具/README.md",
    "工具/scripts/README.md",
    "工具/scripts/clear_pending_delete.py",
    "_安装记录/README.md",
    "_待删除/README.md",
]


def write_new_workspace(base: Path, cleanup_cycle: str, review_cycle: str, log: ActionLog, dry_run: bool) -> None:
    for directory in standard_layout(base):
        ensure_dir(directory, log, dry_run)

    # 同一组占位符传给所有模板；静态模板没有对应 token，原样返回。
    subs = dict(
        mode="new",
        cleanup_cycle=cleanup_cycle,
        review_cycle=review_cycle,
        install_time=now_stamp(),
    )
    for rel in NEW_FILES:
        safe_write(base / rel, render(rel, **subs), log, dry_run)
    # 默认预置跨平台 Python 清理器 工具/scripts/clear_pending_delete.py（开箱即用，
    # 不绑定单一系统）。agent 只需按系统挂定时任务；想用 PowerShell .ps1 / shell .sh
    # 的高级写法见 工具/scripts/README.md 与技能 references/cleanup-scripts.md。


def setup_new(target: Path, cleanup_cycle: str, review_cycle: str, log: ActionLog, dry_run: bool) -> None:
    ensure_dir(target, log, dry_run)
    write_new_workspace(target, cleanup_cycle, review_cycle, log, dry_run)


# ---------------------------------------------------------------------------
# adapt 模式：体检 + 可选轻量升级
# ---------------------------------------------------------------------------

ADAPT_SUBDIR = "Agent工作流助手"

# 轻量升级只新增机制类文件（相对路径 = 模板路径），跳过已存在文件，不接管入口。
LIGHT_UPGRADE_FILES = [
    "工作流/_候选流程规则.md",
    "资料库/README.md",
    "资料库/固定规则.md",
    "资料库/账号与权限说明.md",
    "资料库/业务背景.md",
    "资料库/网站入口.md",
    "DOM地图/_DOM地图模板.md",
    "_待删除/README.md",
]


# 体检时跳过的噪音目录（含 adapt 自己的输出目录，避免自指）
_SCAN_NOISE = {".git", "node_modules", "__pycache__", ".venv", "venv",
               "dist", "build", ".idea", ".vscode", ADAPT_SUBDIR}
# 可能充当"入口文档"的文件名（小写匹配；agent 据此做语义对照，不做缺失判定）
_ENTRY_DOC_NAMES = {"readme.md", "agents.md", "agent.md", "claude.md",
                    "gemini.md", "快速入口.md"}

# Agent Workflow OS 的能力清单。注意：这是"能力"，不是"文件名"——
# 目标系统用什么名字、什么实现来满足它，由 agent 读内容判定，脚本不猜。
_CAPABILITIES = [
    "入口链 / 启动顺序（agent 进来先读什么、按什么顺序）",
    "路由分流（按任务熟悉度决定这次读多少，省 token）",
    "执行记录 / 操作日志（每次任务留痕）",
    "周期复盘（把日志压缩回流程；无论叫巡查 / 复盘 / retro）",
    "网页/外部系统操作记忆（DOM 地图 / playbook / 录制重放 / 视觉捕获，任一即可）",
    "工作流可交接性 / 新 agent 接手验证（只按文档能否跑通最小样本）",
    "知识库 / 固定背景资料（规则、账号、入口、链接）",
    "清理边界 / 回收区（哪些永不删；丢弃走回收而非直删）",
    "风险动作确认（提交 / 付款 / 删除 / 不可逆前先确认）",
]


def _scan_tree(target: Path, max_depth: int = 3, max_lines: int = 120) -> str:
    """递归列出目录结构作为证据（不分类、不判缺）。一层检测看不到藏在子目录里的等价物，故递归。"""
    lines: list[str] = []

    def walk(d: Path, depth: int) -> None:
        if depth > max_depth or len(lines) >= max_lines:
            return
        try:
            entries = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except OSError:
            return
        for p in entries:
            if len(lines) >= max_lines:
                lines.append("  " * depth + "- … （已截断）")
                return
            if p.name in _SCAN_NOISE or p.name.startswith("."):
                continue
            indent = "  " * depth
            if p.is_dir():
                try:
                    n = sum(1 for _ in p.iterdir())
                except OSError:
                    n = 0
                lines.append(f"{indent}- `{p.name}/` （{n} 项）")
                walk(p, depth + 1)
            else:
                lines.append(f"{indent}- `{p.name}`")

    walk(target, 0)
    return "\n".join(lines) if lines else "- （目录为空）"


def _find_entry_docs(target: Path, max_depth: int = 2) -> list[str]:
    """找出可能充当入口/说明文档的文件，供 agent 必读。只列证据，不判缺。"""
    found: list[str] = []

    def walk(d: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = sorted(d.iterdir())
        except OSError:
            return
        for p in entries:
            if p.name in _SCAN_NOISE or p.name.startswith("."):
                continue
            if p.is_dir():
                walk(p, depth + 1)
            elif p.name.lower() in _ENTRY_DOC_NAMES:
                found.append(str(p.relative_to(target)))

    walk(target, 0)
    return found


def existing_observation(target: Path) -> tuple[str, list[str]]:
    """采集证据：递归结构 + 入口文档清单。不做 found/missing 判定——那是 agent 读内容后的事。"""
    return _scan_tree(target), _find_entry_docs(target)


def workflow_health_report(target: Path, mode: str) -> str:
    """生成体检报告的"半成品"：脚本只填证据，能力对照与结论留给 agent 读内容后补。

    脚本不做语义判断——它不认识同义命名、看不出更强实现、分不清设计取舍和缺口。
    硬编码文件名打卡对自定义命名的成熟系统几乎全是误报，所以这里只采证、搭脚手架。
    """
    tree, entry_docs = existing_observation(target)

    if entry_docs:
        entry_bullets = "\n".join(f"- `{d}`" for d in entry_docs)
    else:
        entry_bullets = ("- 前 2 层未发现 README / AGENTS.md / agent.md / CLAUDE.md。"
                         "agent 需自行判断入口在哪；若确实空白，更适合用 `new`。")

    capability_rows = "\n".join(f"| {c} |  |  |  |" for c in _CAPABILITIES)
    cap_count = len(_CAPABILITIES)
    max_score = cap_count * 3

    return f"""# 现有工作流体检报告（半成品 — 需 agent 读内容后打分）

生成时间: {now_stamp()}
模式: {mode}

> ⚠️ 本脚本只做"证据采集"，**不打分、不做语义判断**。它不认识同义命名、看不出更强的实现、
> 也分不清"设计取舍"和"缺口"。下面的「能力评分表」「总分」「结论」**留空**，必须由 agent
> 读完入口文档后按量规打分填写。**分是 agent 读内容打出来的，不是按文件名打卡得来的。**
>
> 三条硬规则，防止把噪音当缺口、把分打低：
> 1. 命名跟模板不同 ≠ 缺。先找等价物（例：执行记录 可能叫 `观察台/`、`执行日志/`），找到按"有"打分。
> 2. 系统已有更强实现 → 打 3 分，不提"升级建议"（例：已有 launchd 自动清理脚本，就别建议"新增清理脚本"）。
> 3. 只对打 0 分（缺）的能力提建议，且先确认没有等价物。

## 评分量规（每项 0–3，按读到的实际内容打）

- **0 缺**：没有，也没有等价物。
- **1 雏形**：有口头约定 / 零散痕迹，没成文、不可复用。
- **2 成文可用**：有明确文档或目录，能照着用。
- **3 成熟或更强**：已固化 / 自动化，或这条比本模板做得更好。
- **— 不适用**：该系统按设计不需要这条（不计入总分）。

## 已发现的结构（证据，最多 3 层）

{tree}

## 入口文档（agent 必读，打分的依据）

{entry_bullets}

## 能力评分表（agent 读完上面文档后填）

| Agent Workflow OS 能力 | 目标系统里的对应物（位置 / 命名 / 实现方式） | 评分 0–3 / — | 说明 |
|---|---|---|---|
{capability_rows}

## 体检总分（agent 按上表算）

- 计分项数（共 {cap_count} 项，排除打"—"的）: ___ 项
- 实得分: ___ / （3 × 计分项数，本表满分 {max_score}）= ___%
- 成熟度档（按百分比对照）:
  - **< 40% 起步**——多数能力缺或仅雏形，适合系统性补。
  - **40–70% 基本可用**——主干在，细节或闭环有缺，按"缺"项逐条补。
  - **70–90% 成熟**——只剩少量可补，别大改。
  - **> 90% 很成熟**——部分已超过本模板，重点是别画蛇添足，只挑真空白补。
- 一句话评价（给用户看的结论）:

## 结论（agent 仅依据上表填写，不要凭空发挥）

- 真实优点（打 2–3 分的，尤其比模板更强的）:
- 真实缺口（只列打 0 分的）:
- 建议保留:
- 建议补的（只针对打 0 分项，且确认无等价物）:

## 边界

- adapt 默认只体检和打分，不改用户任何文件。
- 不修改、不重命名根目录入口文件（AGENTS.md / README.md / agent.md / CLAUDE.md）。
- 不移动、不重命名现有工作流、日志、操作记忆或工具。
- 不把新增内容塞进成熟任务的默认读取路径。
- 打 0 分的能力，经用户确认后才用 `--apply-light-upgrade` 补，且只补确实缺的那几项。
"""


def light_upgrade(target: Path, log: ActionLog, dry_run: bool) -> None:
    """轻量升级：只新增机制类文件，跳过已存在文件，不接管入口。"""
    base = target / ADAPT_SUBDIR if (target / ADAPT_SUBDIR).is_dir() else target
    for directory in [base / "资料库", base / "DOM地图", base / "_待删除"]:
        ensure_dir(directory, log, dry_run)
    for rel in LIGHT_UPGRADE_FILES:
        safe_write(base / rel, render(rel), log, dry_run)


def setup_adapt(target: Path, cleanup_cycle: str, review_cycle: str, log: ActionLog, dry_run: bool, apply_light_upgrade: bool = False) -> None:
    base = target / ADAPT_SUBDIR
    ensure_dir(base, log, dry_run)
    ensure_dir(base / "_安装记录", log, dry_run)
    install_md = render(
        "_安装记录/README.md",
        mode="adapt",
        cleanup_cycle=cleanup_cycle,
        review_cycle=review_cycle,
        install_time=now_stamp(),
    )
    safe_write(base / "_安装记录" / "README.md", install_md, log, dry_run)
    safe_write(base / "现有工作流体检报告.md", workflow_health_report(target, "adapt"), log, dry_run)
    if apply_light_upgrade:
        light_upgrade(target, log, dry_run)
        log.warn("adapt 已按用户选择生成轻量升级文件；仍未覆盖现有流程。")
    else:
        log.warn("adapt 默认只生成体检报告和改进建议；如用户确认升级，再使用 --apply-light-upgrade。")


# ---------------------------------------------------------------------------
# 初始化报告
# ---------------------------------------------------------------------------

NEW_STRUCTURE_SUMMARY = """## 当前真实结构（精简后）

### 入口文件

- `README.md` — 日常分流路由壳
- `AGENTS.md` — 宪法（启动顺序、文件夹地图、归类默认、清理边界、风险底线、命名规则）
- `快速入口.md` — 唯一路由表（工作流 + 流畅等级 + 读取范围）
- `Agent执行手册.md` — 执行纪律、新任务流程、评分、网页批量规则
- `完整工作手册.md` — 完整系统规则

### 目录结构

- `系统设置/` — 节奏设置.md、风险动作默认规则.md
- `系统索引/` — 工作区地图.md、工作流总览.md、产出归类与命名规范.md、用户纠正处理规则.md、术语表.md
- `资料库/` — 业务背景.md、固定规则.md、网站入口.md（常用链接地图）、账号与权限说明.md
- `DOM地图/` — _DOM地图模板.md
- `工作流/` — _工作流模板.md、_examples模板.md、_候选流程规则.md（空工作区，无预置示例工作流）
- `执行记录/` — _执行记录模板.md；原始记录/（空，真实任务执行后写入）
- `巡查/` — 巡查执行流程.md、_巡查日志模板.md、滚动未决.md（常驻台账，跨巡查滚动的未决项，不丢不回链）；巡查日志/（按日期滚动，最新一份即当前结论，含改动方案+执行统计，对话框确认；旧份长期保留作改动史）
- `临时内容/` — README.md（草稿/中间文件/验证文件区）
- `output/` — README.md（正式产出/验证证据/可复用样例区）
- `归档/` — 已吸收旧材料存放区（旧工作流/旧日志/旧产出）
- `工具/` — README.md；scripts/（默认预置跨平台 clear_pending_delete.py，agent 只需挂定时任务）；checkers/connectors/snippets
- `_安装记录/` — README.md、本初始化报告
- `_待删除/` — README.md（显眼回收区，脚本自动清）
"""


# 装后提示：脚本只生成中文工作区 + 默认清理器；分系统/分语言的收尾由 agent 完成。
# 把这几步打印出来，避免它们只埋在 SKILL.md 里被忽略。
NEXT_STEPS_NEW = """
下一步（agent 收尾，工作区已生成）：
（语言/清理周期/巡查周期本应在运行前就问过用户——见 SKILL.md「What To Ask」。
 下面是收尾和兜底。）
1. 语言：本工作区默认中文。若用户的工作语言不是中文，按 SKILL.md「Localization」
   把生成的文件夹改写成目标语言（脚本不做多语言，这步由你来做）。
2. 清理定时：已预置跨平台 `工具/scripts/clear_pending_delete.py`。先 `--dry-run` 验一次，
   再按系统挂定时：Windows 计划任务 / macOS·Linux cron 或 launchd。
   不想自动清理也行——临时文件就在 `临时内容/` 和 `_待删除/`，用户可手动删；
   `output/`、`归档/`、`执行记录/`、`巡查/` 永不删。
3. 周期兜底：若装前没问、这次用了默认「每周一次」，现在补问用户；要改就改
   `系统设置/节奏设置.md`（脚本不覆盖已写入的值）。
"""


def write_report(target: Path, mode: str, log: ActionLog, dry_run: bool) -> None:
    structure_section = NEW_STRUCTURE_SUMMARY + "\n" if mode == "new" else ""
    report = f"""# Agent Workflow OS 初始化报告

时间: {now_stamp()}
目标目录: `{target}`
模式: {mode}
dry_run: {dry_run}

{structure_section}## Created

{md_list(log.created)}

## Updated

{md_list(log.updated)}

## Skipped

{md_list(log.skipped)}

## Warnings

{md_list(log.warnings)}
"""
    if dry_run:
        print(report)
        return
    report_dir = (target / ADAPT_SUBDIR / "_安装记录") if mode == "adapt" else (target / "_安装记录")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"初始化报告--{file_stamp()}.md"
    report_path.write_text(report.rstrip() + "\n", encoding="utf-8")
    log.add_created(report_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize or adapt an Agent Workflow OS workspace.")
    parser.add_argument("--target", required=True, help="Target folder to initialize or inspect.")
    parser.add_argument("--mode", choices=["new", "adapt"], default="new")
    parser.add_argument("--cleanup-cycle", default="每周一次", help="_待删除/ 自动清理周期。")
    parser.add_argument("--review-cycle", default="每周一次", help="工作流巡查周期。")
    parser.add_argument("--apply-light-upgrade", action="store_true", help="In adapt mode, create lightweight improvement files after user approval.")
    parser.add_argument("--dry-run", action="store_true", help="Print intended actions without writing files.")
    return parser.parse_args()


def main() -> int:
    # Force UTF-8 stdout so the Chinese next-steps/report print predictably even when
    # piped on a non-UTF-8 console (e.g. cp936 on Chinese Windows).
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    log = ActionLog()

    if args.mode == "adapt" and not target.exists():
        raise SystemExit(f"Target does not exist for mode adapt: {target}")

    if args.mode == "new":
        setup_new(target, args.cleanup_cycle, args.review_cycle, log, args.dry_run)
    elif args.mode == "adapt":
        setup_adapt(target, args.cleanup_cycle, args.review_cycle, log, args.dry_run, args.apply_light_upgrade)

    write_report(target, args.mode, log, args.dry_run)
    print(f"[OK] {APP_NAME} initialized in {args.mode} mode at {target}")
    print(f"created={len(log.created)} updated={len(log.updated)} skipped={len(log.skipped)} warnings={len(log.warnings)}")
    if args.mode == "new":
        print(NEXT_STEPS_NEW)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
