/**
 * codeb MCP server —— 让模型自己维护知识库。
 *
 * 设计铁律（与 DESIGN.md 一致）：
 *   1. 本文件**不实现任何知识库逻辑**，只做三件事：声明工具、校验参数、调用 Python 内核。
 *   2. 规则只有一份实现，在 kb.py。这里若需要判断，只能通过 kb.py --json 拿结论。
 *   3. 零依赖：不引 @modelcontextprotocol/sdk，手写 stdio JSON-RPC。
 *      Node 24 可直接运行 .ts，无需构建步骤。
 *
 * 传输：MCP over stdio，每行一个 JSON 对象（\n 分隔，不带 Content-Length 头）。
 */

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
// server.ts 位于 <root>/mcp/，向上一级就是项目根（kb.py 所在处）
const PROJECT_ROOT = resolve(HERE, "..");
const KB_PY = join(PROJECT_ROOT, "kb.py");

const SERVER_INFO = { name: "codeb", version: "1.0.0" };
const PROTOCOL_VERSION = "2024-11-05";

/* ------------------------------------------------------------------ 内核调用 */

interface RunResult {
  code: number;
  stdout: string;
  stderr: string;
}

/**
 * 调用 Python 内核。参数一律走 argv，不拼 shell 字符串——
 * 知识库路径里有中文、空格、反斜杠，拼字符串是最容易出错的做法。
 */
function runPy(entry: string[], args: string[]): Promise<RunResult> {
  return new Promise((resolvePromise) => {
    const child = spawn(process.env.KB_PYTHON || "python", [...entry, ...args], {
      cwd: PROJECT_ROOT,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      windowsHide: true
    });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf-8");
    child.stderr.setEncoding("utf-8");
    child.stdout.on("data", (d: string) => (stdout += d));
    child.stderr.on("data", (d: string) => (stderr += d));
    child.on("error", (err) => {
      resolvePromise({ code: 127, stdout: "", stderr: String(err) });
    });
    child.on("close", (code) => {
      resolvePromise({ code: code ?? 1, stdout, stderr });
    });
  });
}

/** 知识库内核（kb.py）与目录表内核（distill.projtree）两个入口。 */
function runKb(args: string[]): Promise<RunResult> {
  return runPy([KB_PY], args);
}
function runProj(args: string[]): Promise<RunResult> {
  return runPy(["-m", "distill.projtree"], args);
}

/** 取 JSON 结果；非 0 退出码时把 stderr 作为错误抛出。 */
async function pyJson<T = any>(runner: (a: string[]) => Promise<RunResult>,
                               args: string[], label: string): Promise<T> {
  const r = await runner([...args, "--json"]);
  if (r.code !== 0) {
    const msg = (r.stderr || r.stdout || "").trim() || `${label} 退出码 ${r.code}`;
    throw new Error(msg);
  }
  try {
    return JSON.parse(r.stdout) as T;
  } catch {
    throw new Error(`内核返回了非 JSON 输出：${r.stdout.slice(0, 400)}`);
  }
}
const kbJson = <T = any>(args: string[]) => pyJson<T>(runKb, args, "kb");
const projJson = <T = any>(args: string[]) => pyJson<T>(runProj, args, "projtree");

/* ---------------------------------------------------------------- 工具定义 */

type ToolResult = {
  content: Array<{ type: "text"; text: string }>;
  isError?: boolean;
};

function text(value: unknown): ToolResult {
  const body = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  return { content: [{ type: "text", text: body }] };
}

function fail(message: string): ToolResult {
  return { content: [{ type: "text", text: message }], isError: true };
}

interface ToolDef {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  handler: (args: any) => Promise<ToolResult>;
}

const REPO_SCHEMA = {
  type: "string",
  description: "仓库目录名（repo/ 下的一级目录，如 infohub）。省略则跨全部仓库。"
};

const TOOLS: ToolDef[] = [
  {
    name: "tree",
    description:
      "通用的树形浏览工具，两棵树共用：\n" +
      "  view=kb（默认）：知识库架构树——repo/ 下的 md 页，按目录折叠。" +
      "会话开始先调它，再决定读哪页。\n" +
      "  view=source：项目源码目录树——未被 gitignore、且非 repo/ 的源码文件，" +
      "每个文件带一句话介绍和新鲜度（fresh/stale/none）。\n" +
      "默认返回 kb 树，行为与旧的 kb_tree 一致。",
    inputSchema: {
      type: "object",
      properties: {
        view: {
          type: "string", enum: ["kb", "source"], default: "kb",
          description: "看哪棵树：kb=知识库架构树（默认），source=源码目录树"
        },
        depth: { type: "number", description: "展开层数，kb 默认 3，source 默认 2" },
        repo: REPO_SCHEMA,
        path: {
          type: "string",
          description: "source 视图的子树路径，如 distill 或 distill/agent；缩小范围很重要（infohub 有 2.9 万文件）"
        },
        only: {
          type: "string", enum: ["all", "stale", "missing"], default: "all",
          description: "source 视图过滤：stale=介绍过期，missing=未写介绍"
        }
      }
    },
    handler: async (a) => {
      const view = a?.view === "source" ? "source" : "kb";
      if (view === "source") {
        const args = ["tree", ...(a?.path ? [String(a.path)] : [])];
        args.push("--depth", String(a?.depth ?? 2));
        if (a?.only && a.only !== "all") args.push("--only", String(a.only));
        args.push("--nested");
        return text(await projJson(args));
      }
      // kb 视图：与旧 kb_tree 逐字一致
      const args = ["tree"];
      if (a?.depth) args.push("--depth", String(a.depth));
      if (a?.repo) args.push("--repo", String(a.repo));
      return text(await kbJson(args));
    }
  },
  {
    name: "kb_read",
    description:
      "读一页。给 section 时只返回那一节（先 kb_heads 看有哪些节），" +
      "比整页读取省很多 token。page 可写 `infohub/collector/l1-primitives` 或省略仓库前缀。",
    inputSchema: {
      type: "object",
      properties: {
        page: { type: "string", description: "页面路径（相对 repo/，可省略 .md）" },
        section: { type: "string", description: "小节标题（子串匹配，忽略大小写与空白）" }
      },
      required: ["page"]
    },
    handler: async (a) => {
      if (!a?.page) return fail("缺少 page");
      const args = ["read", String(a.page)];
      if (a.section) args.push("--section", String(a.section));
      return text(await kbJson(args));
    }
  },
  {
    name: "kb_heads",
    description: "列出一页的全部标题。用它先看清结构，再决定 kb_read 取哪一节。",
    inputSchema: {
      type: "object",
      properties: {
        page: { type: "string", description: "页面路径（相对 repo/）" }
      },
      required: ["page"]
    },
    handler: async (a) => {
      if (!a?.page) return fail("缺少 page");
      return text(await kbJson(["heads", String(a.page)]));
    }
  },
  {
    name: "kb_search",
    description:
      "全库搜词（对空白不敏感，中英混排有无空格都能命中）。返回命中的页面与行号。" +
      "知道关键词但不知道在哪页时用它。",
    inputSchema: {
      type: "object",
      properties: {
        term: { type: "string", description: "搜索词" },
        repo: REPO_SCHEMA,
        limit: { type: "number", description: "最多返回几个页面，默认 20" }
      },
      required: ["term"]
    },
    handler: async (a) => {
      if (!a?.term) return fail("缺少 term");
      const args = ["search", String(a.term)];
      if (a.repo) args.push("--repo", String(a.repo));
      if (a.limit) args.push("--limit", String(a.limit));
      return text(await kbJson(args));
    }
  },
  {
    name: "kb_where",
    description:
      "上行反查：给定源码文件或目录路径，返回哪些页面用 covers 覆盖了它。" +
      "**写入前的第一步**：有命中就更新那几页，没有命中才新建。" +
      "路径写仓库内相对路径（如 collector/kit/paging.py）。",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string", description: "仓库内的文件或目录路径" },
        repo: REPO_SCHEMA
      },
      required: ["path"]
    },
    handler: async (a) => {
      if (!a?.path) return fail("缺少 path");
      const args = ["where", String(a.path)];
      if (a.repo) args.push("--repo", String(a.repo));
      return text(await kbJson(args));
    }
  },
  {
    name: "kb_pack",
    description:
      "现场装订一份上下文册子：写范围 + 相关知识节 + 源码（全文或大纲）。不落盘，永远最新。\n" +
      "\n" +
      "分成四层取料，预算不够时按「可替代程度」逐层丢弃：\n" +
      "1) 目标源码（单文件超预算时退大纲；目录给每个文件大纲）\n" +
      "2) 知识节：只取点名了目标文件的二级小节，不取整页\n" +
      "3) 兄弟文件大纲：同目录其它文件的签名\n" +
      "4) 计划小节 + 「有意省略」清单\n" +
      "\n" +
      "**目标源码永远最后降级**；每次降级都写进「有意省略」并附取回命令。\n" +
      "输出会自报精度：exact（有页精确认领）/ dir（只到目录）/ none（无人认领）。\n" +
      "精度 none 不是失败，是产出待办：这个范围该补一页。\n" +
      "\n" +
      "scope 写仓库内相对路径（文件或目录），如 collector/kit/paging.py。\n" +
      "仓库代码位置来自各仓库页面 frontmatter 的 root:；没写则退回知识库根的兄弟目录。",
    inputSchema: {
      type: "object",
      properties: {
        scope: { type: "string", description: "代码路径（文件或目录），相对仓库根" },
        budget: {
          type: "number",
          description:
            "token 预算（默认 13000）。超了按可替代程度逐层丢，并把丢掉的东西写进「有意省略」。"
        },
        noSource: {
          type: "boolean",
          description:
            "只装知识层，不装源码。问「改这个有哪些坑」时用它：源码常占 70% 以上，" +
            "而这个问题的答案不在源码里。实测单文件从 6968 降到 1764 tok。"
        }
      },
      required: ["scope"]
    },
    handler: async (a) => {
      if (!a?.scope) return fail("缺少 scope");
      const args = ["pack", String(a.scope)];
      if (typeof a?.budget === "number" && a.budget > 0) {
        args.push("--budget", String(a.budget));
      }
      if (a?.noSource === true) args.push("--no-source");
      return text(await kbJson(args));
    }
  },
  {
    name: "kb_dispatch",
    description:
      "派发前的检查：把 N 个写范围放一起，回答四件事。\n" +
      "\n" +
      "- 写范围两两是否冲突（非空就**不能并行派发**，会互相覆盖）\n" +
      "- 共享知识：哪些知识页被多个范围共同认领 —— 这些页每个包都必须装\n" +
      "- 接口面：你写范围内的文件，还被哪些**别人的**页描述 —— 改签名要通知对方\n" +
      "- 串行点：由别的脚本生成的派生文件（如 capabilities.json）—— 同批只能一人重生成\n" +
      "\n" +
      "「写范围之外的派生物」这一项尤其要注意：它不在你的写范围里，\n" +
      "但改完你的文件后必须重跑生成器，否则新内容在派生清单里静默消失。",
    inputSchema: {
      type: "object",
      properties: {
        scopes: {
          type: "array",
          items: { type: "string" },
          description: "两批以上要并行的写范围（仓库内相对路径）"
        }
      },
      required: ["scopes"]
    },
    handler: async (a) => {
      if (!Array.isArray(a?.scopes) || a.scopes.length === 0) return fail("缺少 scopes");
      return text(await kbJson(["dispatch", ...a.scopes.map(String)]));
    }
  },
  {
    name: "kb_route",
    description:
      "按**路由规格**装订：成员集 + 每成员保真度。装订单位比 kb_pack 更细，也更准。\n" +
      "\n" +
      "什么时候用它而不是 kb_pack：你要的是一组「跨目录、各自要看不同程度」的文件。\n" +
      "kb_pack 装目录时按「预算 ÷ 文件数」平分额度，实测 200k 预算下 apps/web 的\n" +
      "43 个文件里仍有 19 个大文件被降级成大纲（含 20111 tok 的 QuestionPanel）——\n" +
      "给了预算也拿不到原文。路由把保真度交给调用方决定。\n" +
      "\n" +
      "role 三档：\n" +
      "- full    全文（原文进上下文）\n" +
      "- index   函数级索引，正文用 read_block 按需取（省一半以上，适合 api.ts 这类巨型文件）\n" +
      "- outline 只有签名行\n" +
      "\n" +
      "**不变式：成员清单永不丢。** 超预算时默认拒绝装订并打印明细（超多少、每成员多少），\n" +
      "只有显式 degrade=true 才按 full→index→outline 降档，并在包顶写警告。\n" +
      "理由：悄悄降一档，答案就基于大纲而不是原文，而它长得像装订成功。\n" +
      "\n" +
      "两种用法：\n" +
      "1) specPath：给规格文件（{repo, entry, budget, members[], questions[]}）\n" +
      "2) around：只**提议**成员、不装订，返回每个候选的 tok 与建议 role\n" +
      "\n" +
      "**定位/计数类问题不要靠装订回答**：实测模型在 155k 上下文里数不准（0/3），\n" +
      "即使给 grep 原始命中仍只有 1/3。那类问题要用 grep_count / find_line 工具。",
    inputSchema: {
      type: "object",
      properties: {
        specPath: {
          type: "string",
          description: "路由规格 JSON 路径（与 around 二选一）"
        },
        around: {
          type: "string",
          description:
            "入口文件路径：只提议候选成员（tok / 建议 role / 被谁 import），不装订"
        },
        depth: {
          type: "number",
          description: "around 的 import 深度，默认 1。实测深度 2 会经由 api.ts 拉进整个 API 表面"
        },
        budget: { type: "number", description: "覆盖规格里的 token 预算" },
        degrade: {
          type: "boolean",
          description:
            "超预算时允许自动降档。默认 false = 拒绝装订并报明细（推荐先看明细再决定）"
        }
      }
    },
    handler: async (a) => {
      const hasSpec = typeof a?.specPath === "string" && a.specPath.length > 0;
      const hasAround = typeof a?.around === "string" && a.around.length > 0;
      if (hasSpec === hasAround) {
        return fail("必须且只能给一个：specPath（装订）或 around（提议）");
      }
      const args = ["route"];
      if (hasSpec) args.push("--spec", String(a.specPath));
      if (hasAround) {
        args.push("--around", String(a.around));
        if (typeof a?.depth === "number") args.push("--depth", String(a.depth));
      }
      if (typeof a?.budget === "number" && a.budget > 0) {
        args.push("--budget", String(a.budget));
      }
      if (a?.degrade === true) args.push("--degrade");
      return text(await kbJson(args));
    }
  },
  {
    name: "kb_upsert",
    description:
      "写入知识库：命中即更新、miss 即补充。这是模型维护知识库的**唯一写入口**。\n" +
      "\n" +
      "四种用法：\n" +
      "1) 新建（miss）：给 repo + title（+ 可选 topic 折叠到子目录）+ body + covers。\n" +
      "2) 替换某节（命中）：给 page + section + body。section 不存在时自动追加该节。\n" +
      "3) 追加（命中）：给 page + append=true + body，正文加到文末。\n" +
      "4) 细粒度替换（命中）：给 page + find + body（换成什么）。只换命中的字面文本，" +
      "其余正文逐字节保留——改一个数字、一句话、一个词时用这个，不要用整页 replace。\n" +
      "\n" +
      "细粒度替换的 find 是**字面匹配**（不忽略空白、不认正则），先 kb_read/kb_search 确认原文。" +
      "强烈建议同时给 expect=预期命中数：命中数与它不符会整体中止，避免「以为改了一处、实际改了七处」。\n" +
      "\n" +
      "调用前先用 kb_where 查覆盖，避免建出重复页。covers 写仓库内相对路径，" +
      "目录以 / 结尾表示前缀匹配（如 collector/kit/）。",
    inputSchema: {
      type: "object",
      properties: {
        page: { type: "string", description: "目标页（命中时必填，相对 repo/）" },
        repo: { type: "string", description: "仓库目录名（新建时必填）" },
        topic: {
          type: "string",
          description: "新建时折叠到的子目录，英文小写（如 collector）。不要平铺在仓库根。"
        },
        title: { type: "string", description: "新建时的页面标题（中文）" },
        section: { type: "string", description: "更新时：要替换或新建的小节标题" },
        append: { type: "boolean", description: "更新时：追加到文末而不是替换某节" },
        replace: { type: "boolean", description: "更新时：整页替换（慎用，会丢掉未写进 body 的节）" },
        find: {
          type: "string",
          description:
            "更新时：要替换的**字面文本**。只替换命中的片段，页面其余内容原样保留。" +
            "配合 body 给出替换值；body 传空串表示删除该文本。"
        },
        expect: {
          type: "number",
          description:
            "与 find 联用：命中数必须正好等于它，否则中止不写入。改多处时用它防止误改。"
        },
        covers: {
          type: "array",
          items: { type: "string" },
          description: "覆盖的源码路径，用于 kb_where 反查"
        },
        body: { type: "string", description: "Markdown 正文（find 模式下是替换值）" },
        bodyFile: {
          type: "string",
          description:
            "正文文件路径（与 body 二选一）。正文很长时优先用它，避免超出单次调用的长度限制。"
        }
      }
    },
    handler: async (a) => {
      const args = ["upsert"];
      if (a?.page) args.push(String(a.page));
      if (a?.repo) args.push("--repo", String(a.repo));
      if (a?.topic) args.push("--topic", String(a.topic));
      if (a?.title) args.push("--title", String(a.title));
      if (a?.section) args.push("--section", String(a.section));
      if (a?.append) args.push("--append");
      if (a?.replace) args.push("--replace");
      // find 是细粒度替换模式：内核按 --find 分支处理，与 --replace（整页）互斥。
      if (typeof a?.find === "string" && a.find.length > 0) {
        args.push("--find", a.find);
        if (typeof a?.expect === "number") args.push("--expect", String(a.expect));
        // find 模式必须显式传替换值：空串 = 删除。
        if (typeof a?.body === "string") {
          args.push("--body", a.body);
        } else if (a?.bodyFile) {
          args.push("--body-file", String(a.bodyFile));
        } else {
          return fail("find 模式下必须给 body（空串表示删除命中文本）或 bodyFile");
        }
        if (Array.isArray(a?.covers) && a.covers.length) {
          args.push("--covers", ...a.covers.map(String));
        }
        return text(await kbJson(args));
      }
      if (Array.isArray(a?.covers) && a.covers.length) {
        args.push("--covers", ...a.covers.map(String));
      }
      if (a?.bodyFile) {
        args.push("--body-file", String(a.bodyFile));
      } else if (a?.body) {
        args.push("--body", String(a.body));
      } else {
        return fail("缺少 body 或 bodyFile");
      }
      return text(await kbJson(args));
    }
  }
];

/* ------------------------------------------------------------- JSON-RPC */

interface RpcRequest {
  jsonrpc: "2.0";
  id?: number | string | null;
  method: string;
  params?: any;
}

function send(obj: unknown): void {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

function reply(id: RpcRequest["id"], result: unknown): void {
  send({ jsonrpc: "2.0", id, result });
}

function replyError(id: RpcRequest["id"], code: number, message: string): void {
  send({ jsonrpc: "2.0", id, error: { code, message } });
}

async function handle(req: RpcRequest): Promise<void> {
  const { id, method, params } = req;

  switch (method) {
    case "initialize":
      reply(id, {
        protocolVersion: PROTOCOL_VERSION,
        capabilities: { tools: { listChanged: false } },
        serverInfo: SERVER_INFO
      });
      return;

    case "notifications/initialized":
      return; // 通知无需回复

    case "ping":
      reply(id, {});
      return;

    case "tools/list":
      reply(id, {
        tools: TOOLS.map((t) => ({
          name: t.name,
          description: t.description,
          inputSchema: t.inputSchema
        }))
      });
      return;

    case "tools/call": {
      const name = params?.name;
      const tool = TOOLS.find((t) => t.name === name);
      if (!tool) {
        replyError(id, -32602, `未知工具：${name}`);
        return;
      }
      try {
        const result = await tool.handler(params?.arguments ?? {});
        reply(id, result);
      } catch (err) {
        reply(id, fail(err instanceof Error ? err.message : String(err)) as any);
      }
      return;
    }

    default:
      if (id !== undefined && id !== null) {
        replyError(id, -32601, `未实现的方法：${method}`);
      }
  }
}

function main(): void {
  if (!existsSync(KB_PY)) {
    process.stderr.write(`[codeb] 找不到内核：${KB_PY}\n`);
    process.exit(1);
  }

  let buffer = "";
  process.stdin.setEncoding("utf-8");
  process.stdin.on("data", (chunk: string) => {
    buffer += chunk;
    let nl: number;
    while ((nl = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, nl).trim();
      buffer = buffer.slice(nl + 1);
      if (!line) continue;
      let req: RpcRequest;
      try {
        req = JSON.parse(line);
      } catch {
        replyError(null, -32700, "无法解析的 JSON");
        continue;
      }
      void handle(req);
    }
  });

  process.stderr.write(`[codeb] MCP server 就绪（stdio），内核 ${KB_PY}\n`);
}

main();
