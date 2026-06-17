#!/usr/bin/env python3
"""清空工作区 _待删除/ 目录内容。output/归档/执行记录/巡查 永不在清理范围。

跨平台：macOS / Linux / Windows 共用这一份。
手动预览： python clear_pending_delete.py --dry-run
手动清理： python clear_pending_delete.py
定时清理：见 工具/scripts/README.md（Mac 用 cron/launchd，Windows 用计划任务）。
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

KEEP = {"README.md", "_清理日志.txt"}
FORBIDDEN = {"output", "归档", "执行记录", "巡查"}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # stable Chinese output when piped
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent.parent          # 工具/scripts/ 的上两级 = 工作区根
    pending = root / "_待删除"

    if not pending.is_dir():
        print("[clear] _待删除/ 不存在，无需清理。")
        return 0

    pending = pending.resolve()
    # 安全护栏
    if pending == root or root not in pending.parents and pending != root / "_待删除":
        print("[clear] 安全检查失败，已中止。")
        return 1
    if any((root / f) == pending or (root / f) in pending.parents for f in FORBIDDEN):
        print("[clear] 拒绝清理受保护目录，已中止。")
        return 1

    targets = [p for p in pending.iterdir() if p.name not in KEEP]
    count = len(targets)
    if args.dry_run:
        print(f"[DryRun] 以下 {count} 项将被删除（实际未删除）：")
        for p in targets:
            print("  ", p)
    else:
        import shutil
        for p in targets:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
        print(f"[clear] 已删除 {count} 项。")

    log = pending / "_清理日志.txt"
    mode = "DryRun" if args.dry_run else "Delete"
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{ts}  mode={mode}  deleted={count}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
