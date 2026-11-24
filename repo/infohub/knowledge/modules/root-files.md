---
covers:
  - sizes.py
  - src/app.d.ts
  - src/hooks.server.ts
title: Root-Level Files Module (Layer 3)
updated: 2026-11-24
---

# 模块：根级文件——部件细页表（第3层）

**项目**：infohub
**源码文件**：`sizes.py`、`src/app.d.ts`、`src/hooks.server.ts`
**第4层语义块索引**：
- `sizes.py`: `../symbols/sizes.py.md`
- `src-app.d.ts`: `../symbols/src-app.d.ts.md`
- `src-hooks.server.ts`: `../symbols/src-hooks.server.ts.md`
**写范围**：root-files
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
不属于任何子目录的根级与 src 顶层文件：全局尺寸常量、类型声明与 SvelteKit 钩子。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `count_lines@34` | def | L34-45 | 按 LF 计行，与编辑器显示一致；读 utf-8-sig 去掉可能的 BOM。 | def count_lines(p: Path) -> int: |
| `walk_files@48` | def | L48-55 |  | def walk_files(base: Path, exts: set[str] \ |
| `human@73` | def | L73-74 |  | def human(n: int) -> str: |
| `cmd_path@77` | def | L77-97 |  | def cmd_path(target: str) -> dict: |
| `Window@18` | interface | L18-20 |  | interface Window { |
| `init@12` | function | L12-15 | 在线模式的启动钩子。 | export async function init() { |

> 本模块共 **9** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="sizes.py", key="count_lines@34")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/app.d.ts", key="Window@18")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/hooks.server.ts", key="init@12")
```
