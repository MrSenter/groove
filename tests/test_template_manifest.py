#!/usr/bin/env python3
"""Guard the template/manifest invariant the initializer relies on.

The script (scripts/init_agent_workflow.py) owns the layout and the file
manifest (NEW_FILES / LIGHT_UPGRADE_FILES); the file *contents* live under
templates/. If a manifest path has no template, `new` crashes on a fresh run;
if a template is orphaned, it ships dead weight. This test enforces both
directions so a future template edit can't silently break `new`.

Run with either:
    python tests/test_template_manifest.py
    pytest tests/test_template_manifest.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "init_agent_workflow.py"
TEMPLATES = ROOT / "templates"


def _load_script():
    spec = importlib.util.spec_from_file_location("init_agent_workflow", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclass resolution needs the module registered
    spec.loader.exec_module(mod)
    return mod


def _all_template_files() -> set[str]:
    return {
        p.relative_to(TEMPLATES).as_posix()
        for p in TEMPLATES.rglob("*")
        if p.is_file()
    }


def test_manifest_paths_have_templates() -> None:
    """Every NEW_FILES / LIGHT_UPGRADE_FILES path must exist under templates/."""
    mod = _load_script()
    manifest = set(mod.NEW_FILES) | set(mod.LIGHT_UPGRADE_FILES)
    missing = sorted(rel for rel in manifest if not (TEMPLATES / rel).is_file())
    assert not missing, f"manifest paths with no template: {missing}"


def test_no_orphan_templates() -> None:
    """Every template file must be referenced by the manifest (no dead weight)."""
    mod = _load_script()
    manifest = set(mod.NEW_FILES) | set(mod.LIGHT_UPGRADE_FILES)
    orphans = sorted(_all_template_files() - manifest)
    assert not orphans, f"templates not referenced by any manifest: {orphans}"


if __name__ == "__main__":
    test_manifest_paths_have_templates()
    test_no_orphan_templates()
    print("[OK] template/manifest invariant holds (both directions).")
