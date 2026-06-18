#!/usr/bin/env python3
"""Behavior checks for the initializer's low-risk contracts.

Run with either:
    python tests/test_initializer_behavior.py
    pytest tests/test_initializer_behavior.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "init_agent_workflow.py"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _run_initializer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=True,
    )


def test_new_dry_run_includes_default_cleaner() -> None:
    """`new --dry-run` should advertise the shipped cross-platform cleaner."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "workspace"
        result = _run_initializer("--target", str(target), "--mode", "new", "--dry-run")
    assert "工具/scripts/clear_pending_delete.py" in result.stdout


def test_cleanup_dry_run_keeps_pending_contents_and_writes_log() -> None:
    """The cleaner dry-run reports targets, keeps files, and writes an audit line."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "workspace"
        _run_initializer("--target", str(target), "--mode", "new")

        pending = target / "_待删除"
        old_file = pending / "old.md"
        old_dir = pending / "old_dir"
        old_file.write_text("discard me\n", encoding="utf-8")
        old_dir.mkdir()
        (old_dir / "nested.txt").write_text("discard me too\n", encoding="utf-8")

        cleaner = target / "工具" / "scripts" / "clear_pending_delete.py"
        result = subprocess.run(
            [sys.executable, str(cleaner), "--dry-run"],
            cwd=target,
            env=_env(),
            text=True,
            capture_output=True,
            check=True,
        )

        assert "[DryRun]" in result.stdout
        assert old_file.exists()
        assert old_dir.exists()
        log = pending / "_清理日志.txt"
        assert "mode=DryRun" in log.read_text(encoding="utf-8")


def test_adapt_default_prints_scorecard_without_writing_report() -> None:
    """Default adapt is dialogue-first and does not create report files."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "existing"
        target.mkdir()
        (target / "README.md").write_text("# Existing workflow\n", encoding="utf-8")

        result = _run_initializer("--target", str(target), "--mode", "adapt")

        assert "Groove 体检评分卡" in result.stdout
        assert "README.md" in result.stdout
        assert not (target / "Agent工作流助手" / "现有工作流体检报告.md").exists()
        assert not (target / "Agent工作流助手" / "_安装记录").exists()


def test_adapt_write_health_report_keeps_archival_scaffold_optional() -> None:
    """The report scaffold is opt-in for archival handoff."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "existing"
        target.mkdir()
        (target / "README.md").write_text("# Existing workflow\n", encoding="utf-8")

        _run_initializer("--target", str(target), "--mode", "adapt", "--write-health-report")

        assert (target / "Agent工作流助手" / "现有工作流体检报告.md").exists()
        assert (target / "Agent工作流助手" / "_安装记录").exists()


def test_adapt_light_upgrade_does_not_overwrite_existing_assistant_files() -> None:
    """Light upgrade may add missing files but must skip files already present."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "existing"
        existing_file = target / "Agent工作流助手" / "资料库" / "README.md"
        existing_file.parent.mkdir(parents=True)
        existing_file.write_text("keep this exact content\n", encoding="utf-8")

        _run_initializer(
            "--target",
            str(target),
            "--mode",
            "adapt",
            "--apply-light-upgrade",
        )

        assert existing_file.read_text(encoding="utf-8") == "keep this exact content\n"


if __name__ == "__main__":
    test_new_dry_run_includes_default_cleaner()
    test_cleanup_dry_run_keeps_pending_contents_and_writes_log()
    test_adapt_default_prints_scorecard_without_writing_report()
    test_adapt_write_health_report_keeps_archival_scaffold_optional()
    test_adapt_light_upgrade_does_not_overwrite_existing_assistant_files()
    print("[OK] initializer behavior checks passed.")
