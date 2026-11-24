---
covers:
  - kb.py
updated: 2026-11-18
---

# Page format and matching rules

页面格式和匹配规则是工具里**唯二**有硬约束的地方。其余（目录怎么分、每页多长、写什么）
全部自由。

## Minimum page format

一个 `.md` 文件，里面**至少有一个标题**。

```markdown
# Page title

正文。
```

就这些。没有必需段落，没有 TL;DR，没有固定小节名。

## How the title is taken

工具把**正文里遇到的第一个标题**当作页面标题。所以：

- 首行写 `# 一句话说清这页是什么`，`kb tree` 输出的就是这个。
- **不用 frontmatter 里的 `title:`**，避免同一件事写两遍。

这条看似琐碎，但它消除了一整类不一致：frontmatter 的 `title` 与正文首行标题
一旦不同，`kb tree` 显示哪个、`kb read` 返回哪个、`covers` 反查时列哪个，
三者可能来自不同来源。只有一个来源，就没有这个问题。

标题的匹配（`--section`）**忽略大小写与空白**，所以 `--section paging` 与
`--section "Paging: judge by"` 等价。

## The only metadata with meaning: `covers`

## The two metadata fields that carry meaning: `covers` and `parent`

```markdown
---
covers:
  - src/loggrep/filter.py
  - src/loggrep/

---

# Filter and render
```

`covers` 只有一用途：**从源码文件向上反查**（`kb where`）。
它不是「这页提到过这些文件」，而是「这些文件的事归这页管」。

`parent` 唯一用途是**记录拆分来源**（`kb tree` 折叠显示），见下一节。
除这两个之外，其余 frontmatter 键（`tags` 等）kb 不解释，但会原样保留。

## Three forms, three behaviours

| 写法 | 含义 | 例 |
| :-- | :-- | :-- |
| `collector/kit/paging.py` | 精确匹配该文件 | 只有这一个文件命中 |
| `collector/kit/` | **按路径段前缀**匹配 | `collector/kit/http.py` 命中；`collector/kit2/x.py` **不**命中 |
| `paging.py` | 后缀匹配 | 任何路径下的 `paging.py` 都命中 |

**尾斜杠是前缀匹配的唯一标志。** 不带斜杠也不带目录的裸文件名走后缀匹配，
而不是「当前目录下的这个文件」——因为 `covers` 里写的是**仓库内相对路径**，
「当前目录」这个概念不存在。

## Why prefix matching is by path segment, not by string

这是最容易写错的一处。`collector/kit/` 必须匹配 `collector/kit/http.py`，
但**不能**匹配 `collector/kit2/x.py`。

若按字符串前缀实现，`collector/kit/` 会命中 `collector/kit2/`——
因为 `"collector/kit2/x.py".startswith("collector/kit")` 为真。

这不是理论问题：任何名字互为前缀的兄弟目录都会串（`src/` 与 `src2/`、
`test/` 与 `tests/`）。串了之后 `kb where` 会返回不相关的页，
而返回不相关的页比返回空更糟——它让人以为这块已经有说明了。

实现上必须先把两边按 `/` 切开、逐段比较，不能对拼接后的字符串做前缀判断。

## Directory-level covers is how aggregation works

总览页写 `covers: [src/]`，就能被这个仓库下**任何文件**的查询命中；
具体的模块页写精确路径。两者同时命中时，结果先列具体页。

这就是「向上聚合」的全部机制——**没有 parent/children 关系，没有 manifest**。
层级是由 `covers` 的粒度自然形成的：目录级 covers 是上一层，精确路径是下一层。

好处是不会出现「父子关系登记了但实际不符」的问题，因为父子关系根本不是被登记的东西，
它是每次查询现场算出来的。

## A known limitation

`covers` 写错路径**不会报错**，只会让 `kb where` 查不到。

这是刻意的：`covers` 描述的是**意图**（「这些文件归我管」），
不该被当作「引用的文件必须存在」的断言。留空或写错都不影响工具运行，
只影响反查能不能命中——而这个后果是局部且容易发现的（查不到就补一页）。

### `parent`：拆分来源，不是唯一归属

页面变大时把它拆成「根页 + 子页」，子页用 `parent` 记下自己是从哪一页拆出来的：

```yaml
---
parent: infohub/collector
covers:
  - collector/kit/
---
```

`kb tree` 会把子页折叠显示在父页下面（`--flat` 关掉折叠，回到纯目录树）。

三条要点，都是为了避免把它用成层级树：

- **`parent` 表达「拆分来源」，不表达「归属」**。一个源文件天然被多个页面从不同角度描述（实测 `infohub/pitfalls` 通过共享 covers 连到 12 个页面），强行规定唯一父节点会逼人删掉正确的知识。
- **弱引用**：指向不存在的页不阻断，`kb tree` 末尾汇总报警。与 `covers` 同一态度——「意图不是存在断言」。但必须报出来：静默忽略会让「拆了一半」的页看起来像正常顶层页。
- **页间多对多关系交给 `kb graph`**，不要塞进多个 `parent`。多值 parent 会让人以为能表达任意层级，最后塌成一张乱网。

拆分后父页应保留一段**路由表**（3–5 行：去哪个子页、为什么），而不是清空。完全清空会让读者从入口直接跳崖。

### 写盘会保留你不认识的 frontmatter 键

`upsert` 会把 `parent`、`tags` 等键原样写回，`_write_page` 用 `extra` 承接不认识的键。

这条是修过的缺陷：早期版本只写 `covers`，**任何一次编辑都会把 `parent`/`tags` 静默抹掉**——元数据在第一次 upsert 时就丢了，且毫无提示。新增 frontmatter 字段时务必确认 `_write_page` 的 `extra` 路径能带它过去。

### `root`：坐标，不是分类

每个仓库**在一个页面**的 frontmatter 写一行，指出它的代码在磁盘上的位置：

```yaml
root: D:/work/project/knowledge_map/atomkgraph
```

它只用来让 `kb pack` / `kb dispatch` 找到源码。`covers` 写的是**仓库内相对路径**，
但仓库根在哪里推不出来——`atomkgraph` 的代码不在 `D:/work/project/atomkgraph`，
而在 `knowledge_map/` 下面。

这跟本项目反对 `manifest.toml` 的理由不冲突，因为**性质不同**：

- `manifest.toml` 是分类，用来决定「哪些知识属于哪层」。填错了没人看得出来，
  而且它跟页面内容重复，必须手工同步——那才是失败的原因。
- `root` 是坐标。填错了 `kb pack` 立刻报「scope 定位不到磁盘根」并列出已知映射，
  **每次调用都会验证一次**。它不承载任何分类信息。

实测差异：朴素按「知识库根的兄弟目录」推断，163 条 covers 里 49 条指向不存在的路径；
写显式 `root` 后 223 条页级 covers 里 217 条可解析。
