---
covers:
  - scripts/output/make_packet_timing.py
title: Semantic block index: make_packet_timing.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：make_packet_timing.py（第4层）

**源码文件**：`scripts/output/make_packet_timing.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="scripts/output/make_packet_timing.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| vbrace@29 | def | L29-45 | 竖直花括号：贴在竖线 x 旁，开口朝向线段（side='left'/'right' 指花括号在线的哪一侧）。 | def vbrace(x, y1, y2, bulge, side): |
| add_brace@47 | def | L47-56 |  | def add_brace(ax, x, y1, y2, text, side="right", bulge=0.18, color="#2… |
| band@58 | def | L58-85 | 画一段分组时空平行四边形：头部 (x1,t_head)->(x2,t_head+prop)，尾部下方 send。 | def band(ax, x1, x2, t_head, prop, send, label, fill="#dbe4f0", head_d… |
| draw_scenario@87 | def | L87-118 |  | def draw_scenario(ax, title, with_trans=False, with_queue=False): |
