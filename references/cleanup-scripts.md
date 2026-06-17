# 清理脚本模板（按系统选一份）

`new` 模式**不**预置清理脚本。生成工作区后，由 agent 按目标系统把下面对应的一份写到
`工具/scripts/` 下。三份行为一致：只清空工作区根下的 `_待删除/`（保留 `README.md` 和
`_清理日志.txt`），拒绝工作区根 / 区外路径 / `output/` / `归档/` / `执行记录/` / `巡查/`，支持 DryRun，
每次运行向 `_待删除/_清理日志.txt` 追加一行。

工作区根 = 脚本所在 `工具/scripts/` 的上两级。

---

## A. 跨平台 Python（推荐，Mac + Windows 同一份）

写到 `工具/scripts/clear_pending_delete.py`，用 `python3 clear_pending_delete.py [--dry-run]` 调用。
Mac 用 `cron`/`launchd`，Windows 用计划任务，都调这同一个 py。没有 BOM/编码坑。

```python
#!/usr/bin/env python3
"""清空工作区 _待删除/ 目录内容。output/归档/执行记录/巡查 永不在清理范围。"""
import argparse, datetime as dt
from pathlib import Path

KEEP = {"README.md", "_清理日志.txt"}
FORBIDDEN = {"output", "归档", "执行记录", "巡查"}


def main() -> int:
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
```

定时（Mac，每周一 9:00，cron）：
```bash
0 9 * * 1 /usr/bin/python3 "/绝对路径/工具/scripts/clear_pending_delete.py" >> /tmp/clear_待删除.log 2>&1
```

---

## B. Windows PowerShell（公司 Win 机；这份是演示目录里已实测通过的）

写到 `工具/scripts/Clear-待删除.ps1`。**硬约束**：必须 **UTF-8 + BOM** 落盘，且只用 PS 5.1
兼容语法（不要 `?.`、三元 `?:`），否则 PowerShell 5.1 把中文按 ANSI 误读、解析失败。
由 Windows 计划任务定时调用。

```powershell
<#
.SYNOPSIS
    清理工作区 _待删除/ 目录内容。
.DESCRIPTION
    只清理工作区根目录下的 _待删除/ 目录内容。output/、归档/、执行记录/、巡查/ 永不在清理范围。
.PARAMETER DryRun
    仅预览将被删除的内容，不实际删除。
#>
[CmdletBinding()]
param([switch]$DryRun)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = (Resolve-Path (Join-Path $scriptDir '..\..')).Path

function Resolve-SafeTarget {
    param([string]$TargetPath, [string]$RootPath)
    $r = Resolve-Path -LiteralPath $TargetPath -ErrorAction SilentlyContinue
    $resolved = if ($r) { $r.Path } else { $null }
    if (-not $resolved) { return $null }
    if (-not $resolved.StartsWith($RootPath, [System.StringComparison]::OrdinalIgnoreCase)) { return $null }
    if ($resolved -eq $RootPath) { return $null }
    $forbidden = @('output', '归档', '执行记录', '巡查') | ForEach-Object { Join-Path $RootPath $_ }
    foreach ($f in $forbidden) {
        if ($resolved.StartsWith($f, [System.StringComparison]::OrdinalIgnoreCase)) { return $null }
    }
    return $resolved
}

$pendingDelete = Join-Path $workspaceRoot '_待删除'
if (-not (Test-Path -LiteralPath $pendingDelete)) {
    Write-Host "[Clear-待删除] _待删除/ 目录不存在，无需清理。"; exit 0
}
$safeTarget = Resolve-SafeTarget -TargetPath $pendingDelete -RootPath $workspaceRoot
if (-not $safeTarget) { Write-Error "[Clear-待删除] 安全检查失败：目标路径不合法，已中止。"; exit 1 }

$items = Get-ChildItem -LiteralPath $safeTarget -Force -ErrorAction SilentlyContinue |
         Where-Object { $_.Name -ne 'README.md' -and $_.Name -ne '_清理日志.txt' }
$count = ($items | Measure-Object).Count

if ($DryRun) {
    Write-Host "[DryRun] 以下 $count 项将被删除（实际未删除）："
    $items | ForEach-Object { Write-Host "  $($_.FullName)" }
} else {
    $items | Remove-Item -Recurse -Force
    Write-Host "[Clear-待删除] 已删除 $count 项。"
}

$logPath = Join-Path $safeTarget '_清理日志.txt'
$mode = if ($DryRun) { 'DryRun' } else { 'Delete' }
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
"$timestamp  mode=$mode  deleted=$count" | Out-File -FilePath $logPath -Append -Encoding utf8
```

落盘提醒（写文件时）：用会加 BOM 的方式存，例如 Python `path.write_text(content, encoding="utf-8-sig")`，
或 PowerShell `Set-Content -Encoding utf8BOM`（PS5.1 用 `[System.IO.File]::WriteAllText($p,$s,[System.Text.UTF8Encoding]::new($true))`）。

---

## C. macOS / Linux shell（不想用 Python 时）

写到 `工具/scripts/clear-待删除.sh`，`chmod +x`，`cron`/`launchd` 调用。

```bash
#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$script_dir/../.." && pwd)"
pending="$root/_待删除"
dry=0; [ "${1:-}" = "--dry-run" ] && dry=1

[ -d "$pending" ] || { echo "[clear] _待删除/ 不存在，无需清理。"; exit 0; }

count=0
shopt -s dotglob nullglob
for p in "$pending"/*; do
  base="$(basename "$p")"
  [ "$base" = "README.md" ] && continue
  [ "$base" = "_清理日志.txt" ] && continue
  if [ "$dry" = 1 ]; then echo "  $p"; else rm -rf "$p"; fi
  count=$((count+1))
done
mode=$([ "$dry" = 1 ] && echo DryRun || echo Delete)
printf '%s  mode=%s  deleted=%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$mode" "$count" >> "$pending/_清理日志.txt"
echo "[clear] mode=$mode deleted=$count"
```
