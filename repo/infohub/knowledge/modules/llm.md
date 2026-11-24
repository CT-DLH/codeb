---
covers:
  - collector/llm/audience.py
  - collector/llm/extract.py
  - collector/llm/projects.py
  - collector/llm/research.py
title: LLM Extraction Module (Layer 3)
updated: 2026-11-24
---

# 模块：LLM 抽取——部件细页表（第3层）

**项目**：infohub
**源码文件**：`collector/llm/audience.py`、`collector/llm/extract.py`、`collector/llm/projects.py`、`collector/llm/research.py`
**第4层语义块索引**：
- `collector-llm-audience.py`: `../symbols/collector-llm-audience.py.md`
- `collector-llm-extract.py`: `../symbols/collector-llm-extract.py.md`
- `collector-llm-projects.py`: `../symbols/collector-llm-projects.py.md`
- `collector-llm-research.py`: `../symbols/collector-llm-research.py.md`
**写范围**：collector/llm/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
基于 LLM 的内容抽取与研究方向聚合：从原始文本中提取结构化字段与主题。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `plan_audience_input@112` | def | L112-145 | 把评论/弹幕确定性地预筛成一段给 LLM 的文本。 | def plan_audience_input( |
| `summarize_audience@329` | def | L329-429 | 把评论/弹幕归纳成卡片可用的几段。没材料时返回 None（不烧一次 LLM）。 | def summarize_audience( |
| `render_audience_md@432` | def | L432-461 | 把归纳结果渲染成卡片正文的一节。没有内容时返回空串（不写空标题）。 | def render_audience_md(aud: dict[str, Any], *, n_comments: i… |
| `LlmUnavailable@36` | class | L36-37 | 没有凭据 / 重试耗尽 / 输出始终不合法。调用方据此回退正则。 | class LlmUnavailable(RuntimeError): |
| `ExtractResult@41` | class | L41-48 |  | class ExtractResult: |
| `cache_key@75` | def | L75-77 |  | def cache_key(prompt_version: str, model: str, name: str, pa… |
| `cache_get@80` | def | L80-88 |  | def cache_get(key: str) -> tuple[dict[str, Any], str] \ |
| `build_user_prompt@105` | def | L105-108 |  | def build_user_prompt(lines: list[str], offset: int = 0) -> … |
| `normalize_projects@136` | def | L136-191 | 模型输出 → 可用项目条目。纯函数，离线可测。 | def normalize_projects( |
| `extract_projects@194` | def | L194-259 | 一张卡的项目清单 → 项目条目。 | def extract_projects( |
| `plan_queries@120` | def | L120-171 | 决定下一轮检索词。返回 [{query, goal}]。 | def plan_queries( |
| `bridge_terms@209` | def | L209-226 | 要一组跨语言的核心词（中文 + 英文），用于跑题闸判「是否切题」。 | def bridge_terms(topic: str) -> list[str]: |
| `mine_evidence@393` | def | L393-464 | 从一篇正文里挖证据。返回 (证据列表, 校验统计)。 | def mine_evidence( |
| `classify_source@518` | def | L518-543 | 按域名定 primary / secondary / unknown，模型判断只当兜底。 | def classify_source(url: str, model_kind: str = "") -> str: |

> 本模块共 **53** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/llm/audience.py", key="plan_audience_input@112")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/llm/extract.py", key="LlmUnavailable@36")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/llm/projects.py", key="_squash@96")
```
