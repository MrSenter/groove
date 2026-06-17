# scripts

放可复用执行脚本、辅助脚本。

## 清理脚本（_待删除/ 自动清理）

**已默认预置跨平台 Python 清理器：`clear_pending_delete.py`**（一份在 macOS / Linux / Windows
都能跑，无 BOM/编码坑）。开箱即用，agent 只需挂定时任务。

手动用：

```bash
python clear_pending_delete.py --dry-run   # 只预览，不删
python clear_pending_delete.py             # 实际清理
```

定时挂载（按系统选一种）：

- **Windows**：用「任务计划程序」新建任务，操作指向本机 Python + 本脚本绝对路径。
- **macOS / Linux**：cron，例如每周一 9:00：
  `0 9 * * 1 /usr/bin/python3 "/绝对路径/工具/scripts/clear_pending_delete.py"`

不想自动清理也行：临时文件都在 `临时内容/` 和 `_待删除/`，可手动删除。

清理脚本的硬约束（任何实现都一致）：

- 只清空工作区根下的 `_待删除/`；保留其中的 `README.md` 和 `_清理日志.txt`。
- 拒绝清理工作区根、工作区外路径，**绝不碰** `output/`、`归档/`、`执行记录/`、`巡查/`。
- 支持"只预览不删除"（DryRun）。
- 每次运行向 `_待删除/_清理日志.txt` 追加一行：时间、模式、删除数量。

## 想换成 PowerShell / shell 写法？

默认的 Python 版已够用。若你坚持要 PowerShell `Clear-待删除.ps1`（必须 **UTF-8 + BOM** 落盘、
只用 PS 5.1 兼容语法）或 macOS/Linux 的 `clear-待删除.sh`，技能目录
`references/cleanup-scripts.md` 有已实测的现成模板。
