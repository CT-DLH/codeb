---
covers:
  - collector/sites/
updated: 2026-11-21
---

# Collector: the site specs

`collector/sites/` 下的 YAML 按 family 目录分组（`hitsz/` 与 `hit_yzb/`）。它们的价值不在配置本身，
在**注释里那些「不要修正」的站点事实**——每一条都是花时间试出来的，改错不会报错，只会少采。

## hitsz/teachers.yaml：教师主页型（最重的一份）

```yaml
family: hitsz
kind: teacher_home
site: 哈工大教师主页系统
base: https://homepage.hit.edu.cn/
enabled: true
http: {delay: 1.2, timeout: 25, retries: 2}
apis:
  body: TeacherHome/teacherBody.do
  name_search: hompage/findTeachersByName.do      # ← 少一个 e，不是笔误
```

`apis.body` 是**一次 POST 拿全部页签**的接口。页面左侧的「个人介绍 / 科研论文 /
科研项目」是前端页签，但数据由主页 JS 一次 `POST TeacherHome/teacherBody.do` 取回，
响应里已包含全部页签的 HTML——所以不需要驱动浏览器点按钮。

`apis.name_search` 的 `hompage` **少一个 e 是站点的真实路径**，注释原话：
「站点路径就是 hompage（少一个 e），不是笔误，不要『修正』」。
这一条是这份文件里最值钱的注释：任何人看到都会想改，改了按姓名反查就 404。

`selectors.profile` 的全部键：

| 键 | 选择器 | 说明 |
| :-- | :-- | :-- |
| `tid` | `div.teacher-body[data-tid]` | 取 `data-tid` 属性，**后续接口调用的唯一凭据** |
| `name` | `h3.chineseName` | |
| `describe` | `span.user-describe` | 取 `title` 属性优先 |
| `position` | `span.user-position` | 取 `title` 属性优先 |
| `discipline` | `span.user-discipline` | 取 `title` 属性优先 |
| `dept_link` | `a[href*="deptName="]` | 从 href 里正则抠 `deptName=(\d+)` |
| `photo` | `img[data-src]` | 懒加载，`data-src` 优先于 `src` |
| `contact_item` | `li.addr` | 联系方式行容器 |
| `contact_label` | `em` | 行内标签（「邮箱」「电话」「地址」） |
| `contact_value` | `div p` | 行内的值 |
| `email` | `.EmailText` | 联系方式行拿不到时的兜底 |
| `email_reverse` | `true` | **见下** |

`email_reverse: true` 是这份配置里第二重要的键。主页把邮箱**倒着写**
（`nc.ude.tih@…`），页面上由 JS 反转显示。所以采集器读到的原始文本必须自己 `[::-1]`。
没有这条注释的话，下一个人会以为它是冗余配置而删掉，然后所有邮箱都变成乱序字符串——
不报错、不告警，只是数据全错。

`selectors.sections` 的关键项：

```yaml
item: li.con_parts             # 每个页签一个 li
title: .part_t_l em            # 页签名
strip: [".part_t", ".model_title"]   # 抽正文前先删掉标题区
paper_item: li
project_name_prefix: "项目名称"
project_desc_prefix: "项目描述"
```

`aliases` 是这份文件的**主体**：一个按稳定小节名分组的同义词表。
键是卡片里的稳定小节名，值是主页上出现过的写法（包含匹配、大小写不敏感）：

| 稳定小节名 | 举例（完整列表见 YAML） |
| :-- | :-- |
| `个人简介` | 个人介绍 / 个人信息 / 基本信息 / Persional Profile（站点原文拼错的）/ Biography |
| `研究方向` | 研究领域 / 研究兴趣 / Research Areas / Research direction |
| `研究与工作经历` | 工作经历 / 教育经历 / 教育背景 / Work Experience / Education |
| `实验室介绍` | 课题组简介 / 联合实验室 |
| `科研论文` | 发表论文 / 代表性学术论文 / 近5年代表性论文 / Publications / Papers / Journals / Conferences |
| `科研项目` | 科研项目（在研）/ 科研项目（结题）/ Research Projects |
| `专利` | 发明专利 / Patent |
| `科研奖励` | 科研成果及奖励 / 所获奖项 / Awards |
| `专业资质与学术兼职` | Professional Qualification & Academic Service |
| `任教和任导师经历` | 任教与导师经历 / Teaching/Supervising Experience |
| `招生信息` | 招生计划 / 招生简章 / 招聘 / 团队招新 / Recruitment / Application |

注意 `Persional Profile`（拼错的 Persional）和 `opportunity`（小写单数）——别名表里
收的是**站点上真实出现过的原文**，不是正确拼写。改这一列的原则是「只增不改」。

`output` 段有 4 个特殊键：

```yaml
domain: info_mentor        # 三卡制后带家族前缀；写旧名 mentor 会 export 成功但 import 报错
object_type: 导师
source: 哈工大教师主页系统   # 中文名，不是注册名！（注册名是 site_hitsz_teacher_home）
fields:
  title: name
  summary: summary
  source_ref: url
  ext.name_en: name_en      # ext.* 前缀是卡片扩展字段
  ext.dept / ext.discipline / ext.research / ext.email / ext.homepage
  ext.browse_count: browse
  ext.homepage_updated: update_time
  ext.data_flags: flags
  ext.phone / ext.address
body_sections: ["个人简介","研究方向","实验室介绍","研究与工作经历","科研论文","科研项目"]
include_other_sections: true
clear_fields: ["summary","gaps","last_verified","ext.data_flags","ext.research","ext.dept",
               "ext.discipline","ext.email","ext.name_en","ext.browse_count","ext.homepage_updated"]
gaps_from: flags
```

三个容易踩的点：

- `domain: info_mentor` 不能写成 `mentor`。注释原话：「写旧名时 `crawl:export` 能导出、
  `import:jsonl` 会报『未知领域: mentor』——`--check` 查不出这一层」。
- `body_sections` 是**排序**，不是白名单。`include_other_sections: true` 让配置里没点名的
  小节（获奖、专利、招生信息…）接在后面，而不是被丢掉。
- `clear_fields` 的存在理由是「旧值可能是上一次采集的占位」（如「研究方向未在主页披露」），
  必须能撤回再写。少一个字段就会出现「主页已补上，卡片还是占位」。

这份 spec 的 `source: 哈工大教师主页系统` 是**给人看的中文名**。
`collect_site.py --register` 写 `articles.platform` 时用的是注册名
`site_hitsz_teacher_home`，两者不是一回事——写错会让 `queue()` 的 fetchable 过滤判死。

## hitsz/columns.yaml：栏目型（最简的一份）

```yaml
family: hitsz_grad
kind: column_list
site: 哈工大研究生招生网
base: https://yzb.hit.edu.cn/
http: {delay: 1.2, timeout: 25, retries: 1}
seeds: [{url: /, label: 主页}]
paging: {mode: auto, probe_limit: 2}
attach: {mode: auto}
output:
  domain: article
  object_type: 通知
  source: hitsz_column
  fields: {title: title}      # 只有 title，列表型不需要更多
```

这份 spec 的目的**不是采集**，是证明「只写一份 YAML、不碰 L1 / L3 就能接上真实调用方」。
所以它故意用最简形态：`seeds` 指向首页、`paging`/`attach` 都是默认 `auto`、
`output.fields` 只有一个 `title`。

`notes` 里记的实测数据是选站依据（2026-06 实测）：研招网首页是一个正常的内容页、
带大量内容链接，而 `homepage.hit.edu.cn` 根路径只回一个几百字节的重定向壳、0 条链接——
所以第一所学校用研招网而不是教师主页系统。

`paging.probe_limit: 2` 比默认的 3 小一档：这份 spec 是通路验证，不想在探测上花第三次请求。

## hit_yzb/announcement_list.yaml：公告列表型

```yaml
family: hit_yzb
kind: announcement_list
base: https://yzb.hit.edu.cn/       # 与 hitsz_grad 的 columns.yaml 同一个站
seeds: [{url: /, label: 主页}]
paging: {mode: auto, probe_limit: 2}
output:
  domain: article
  object_type: 公告              # ← 与 columns.yaml 的唯一实质差别
  source: hit_yzb_announcement
  fields: {title: title}
```

与 `hitsz/columns.yaml` **同一个站点、同一个 base**，差别只有 `kind` 与 `output`。
这是「两种列表型 kind 同族、复用同一份 L2 组合层」的最直接证据：
`crawl_column()` 里对这两个 kind 没有任何分支。

`notes` 里有一句关键的当前限制：

> `paging` / `attach` 保持默认 auto，不写 pattern（L1 尚未开放 pattern 入参，
> 写了会明确报 `pattern_mode_pending` 而不是静默按 auto 跑）

所以**现在不要在任何 spec 里写 `paging: {mode: pattern}`**，它会让整次采集直接返回空报告
加一条 `pattern_mode_pending` 失败项。

## family 目录与实际注册的源不是一对一

目录里放几份 YAML 与注册出几个源是两件事：`capabilities.json` 的 `sites` 键列的是：

```
site_hit_yzb_announcement_list
site_hitsz_grad_column_list
site_hitsz_teacher_home
```

`hitsz/` 目录下的两份 YAML 注册出两个**不同 family** 的源
（`family: hitsz` 与 `family: hitsz_grad`），所以注册名不是按目录推的，是按
`family` + `kind` 拼的——目录只是分组习惯。数目录里的文件得不到源的数量，
要数就查 `capabilities.json` 的 `sites` 键。

## 写一份新 spec 的检查清单

1. `family` 与 `kind` 决定注册名 `site_<family>_<kind>`。注册名一旦上线，**不要改**——
   `pipeline.db.articles.platform` 里存的是它，改了会让历史行判死。
2. `base` 必须 http(s)，结尾斜杠会被自动补上（`_validate_common` 里 `data["base"] += "/"`），
   所以写 `https://x.edu.cn` 和 `https://x.edu.cn/` 等价，但**写成 `https://x.edu.cn/col/`
   会让后面所有 `urljoin` 的位置全偏**。
3. `kind` 只能是 `teacher_home` / `column_list` / `announcement_list` 三选一，
   写第四个会报 `kind='xxx' 没有对应适配器`。
4. 列表型**不要写 `selectors`**——会被明确报错（防「照教师主页复制粘贴忘了删」）。
5. `output.fields` 必须含 `title`，否则 `SpecError`。
6. `http.delay` 是**站点额外声明**，真正的按 host 限速在 L1。
   写 1.2 是因为这两个站的实测节奏，不是通用值。
7. 加站点后要跑 `python tools/capabilities.py --write` 重新生成 `capabilities.json`，
   否则 TS 侧的 `collect_guide` / 下拉源看不到它。`--check` 会告诉你是否忘了。

## 另见：从主页到简介的完整一遍

本页记的是 spec 的**逐键语义**。把「这份 spec 实际被谁消费、产物怎么一路变成卡片上的
`summary`」串起来的是 `infohub/collector/crawl-db-jsonl-llm`：
`collect_site.py`（`--register` 才写库、teacher_home 不支持 `--out`）→ `crawl.db` →
`crawl:export`（`buildBody` / `buildRecord` / `summary` 兜底 / `_clear` 空值例外）→
`import:jsonl` → `batch_llm` + `mentor-summary-unify.json`。

那页还列了 6 条**写错不报错**的跨层契约（`domain` 必须 `info_mentor`、`source` 是中文显示名
≠ 注册名 `site_hitsz_teacher_home`、`body_sections` 是排序不是白名单、`clear_fields`
新值为空时逐路径不撤、两个库不混用、`email_reverse` 的倒写邮箱）。改 spec 前值得先看。
