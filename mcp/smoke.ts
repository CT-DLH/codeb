/**
 * MCP 端到端冒烟测试：按真实客户端的方式走一遍 stdio 协议。
 * 不联网、不依赖 SDK。用法：node mcp/smoke.ts
 */
import { spawn } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SERVER = join(HERE, "server.ts");

interface Pending {
  resolve: (v: any) => void;
  reject: (e: Error) => void;
}

const child = spawn(process.execPath, [SERVER], {
  stdio: ["pipe", "pipe", "pipe"],
  windowsHide: true
});

child.stderr.setEncoding("utf-8");
let stderr = "";
child.stderr.on("data", (d: string) => (stderr += d));

const pending = new Map<number, Pending>();
let nextId = 1;
let buffer = "";

child.stdout.setEncoding("utf-8");
child.stdout.on("data", (chunk: string) => {
  buffer += chunk;
  let nl: number;
  while ((nl = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, nl).trim();
    buffer = buffer.slice(nl + 1);
    if (!line) continue;
    let msg: any;
    try {
      msg = JSON.parse(line);
    } catch {
      continue;
    }
    const p = pending.get(msg.id);
    if (p) {
      pending.delete(msg.id);
      msg.error ? p.reject(new Error(msg.error.message)) : p.resolve(msg.result);
    }
  }
});

function call(method: string, params?: unknown): Promise<any> {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
    setTimeout(() => {
      if (pending.has(id)) {
        pending.delete(id);
        reject(new Error(`超时：${method}`));
      }
    }, 20000);
  });
}

function notify(method: string, params?: unknown): void {
  child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method, params }) + "\n");
}

function textOf(result: any): string {
  return (result?.content ?? []).map((c: any) => c.text).join("\n");
}

let passed = 0;
let failed = 0;

function check(name: string, ok: boolean, detail = ""): void {
  if (ok) {
    passed++;
    console.log(`  PASS  ${name}`);
  } else {
    failed++;
    console.log(`  FAIL  ${name}${detail ? "  ← " + detail : ""}`);
  }
}

async function main(): Promise<void> {
  console.log("MCP 冒烟测试\n");

  const init = await call("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "smoke", version: "1" }
  });
  check("initialize 返回 serverInfo", init?.serverInfo?.name === "codeb");
  check("声明 tools 能力", init?.capabilities?.tools !== undefined);
  notify("notifications/initialized");

  const list = await call("tools/list");
  const names: string[] = (list?.tools ?? []).map((t: any) => t.name).sort();
  check("tools/list 返回 9 个工具", names.length === 9, `实际 ${names.length}: ${names}`);
  for (const want of ["tree", "kb_read", "kb_heads", "kb_search", "kb_where",
                      "kb_pack", "kb_dispatch", "kb_upsert", "kb_route"]) {
    check(`工具有 ${want}`, names.includes(want));
  }
  check("旧名 kb_tree 已移除", !names.includes("kb_tree"));

  // tree 默认视图 = kb：输出须与旧 kb_tree 逐字一致
  const tree = await call("tools/call", { name: "tree", arguments: {} });
  const treeData = JSON.parse(textOf(tree));
  check("tree(kb) 有页面", treeData.stats.pages > 0, `pages=${treeData.stats.pages}`);
  check("tree(kb) 按目录折叠", treeData.items[0].rel.includes("/"));

  // tree 的 source 视图：源码目录树，嵌套结构，不含 repo/
  const srcTree = await call("tools/call", {
    name: "tree", arguments: { view: "source", depth: 1 }
  });
  const srcData = JSON.parse(textOf(srcTree));
  check("tree(source) 是嵌套树", srcData.view === "source" && Array.isArray(srcData.tree));
  check("tree(source) 不含 repo/", !JSON.stringify(srcData.tree).includes('"repo/"'));
  check("tree(source) 有文件", (srcData.files ?? 0) > 0, `files=${srcData.files}`);

  // 层级正确性只能从文本输出验证：JSON 里没有父子结构。
  // 曾经的缺陷是 `codeb/design/` 被印在 `infohub/` 块下面——所有 rel 都合法，
  // 只有缩进位置错，所以必须检查「缩进后的祖先链」。
  const { execFileSync } = await import("node:child_process");
  const treeText = execFileSync("python", [join(HERE, "..", "kb.py"), "tree"], {
    encoding: "utf-8",
    env: { ...process.env, PYTHONIOENCODING: "utf-8" }
  });
  const stack: Array<{ indent: number; name: string }> = [];
  let nestingOk = true;
  let nestingDetail = "";
  const seenDirs = new Set<string>();
  for (const line of treeText.split("\n")) {
    // 末尾可能有 \r（Windows 下 Python 的文本输出是 CRLF），
    // 所以用 \s*$ 兜住而不是以 $ 紧接 /。
    const m = /^(\s*)(\S+)\/\s*$/.exec(line);
    if (!m) continue;
    const indent = m[1].length / 2;
    while (stack.length && stack[stack.length - 1].indent >= indent) stack.pop();
    const parent = stack[stack.length - 1]?.name;
    const name = m[2];
    seenDirs.add(`${parent ?? "<root>"}/${name}`);
    // design/ 的父目录必须是 codeb，不能是 infohub
    if (name === "design" && parent !== "codeb") {
      nestingOk = false;
      nestingDetail = `design/ 的父目录是 ${parent}`;
    }
    if (name === "collector" && parent !== "infohub") {
      nestingOk = false;
      nestingDetail = `collector/ 的父目录是 ${parent}`;
    }
    stack.push({ indent, name });
  }
  // 同时验证「该出现的子目录确实出现了」——只查父目录正确性的话，
  // 把递归整段删掉（子目录全部消失）也会被判为通过。
  for (const expect of ["codeb/design", "infohub/collector"]) {
    if (!seenDirs.has(expect)) {
      nestingOk = false;
      nestingDetail = `缺少子目录 ${expect}`;
    }
  }
  check("嵌套目录的父目录正确且存在", nestingOk, nestingDetail);
  check(
    "全库页面标题为英文",
    treeData.items.every((i: any) => !/[\u4e00-\u9fff]/.test(i.title)),
    treeData.items.filter((i: any) => /[\u4e00-\u9fff]/.test(i.title)).map((i: any) => i.rel).join(",")
  );
  check(
    "每页都有中文提示",
    treeData.items.every((i: any) => !i.hint || /[\u4e00-\u9fff]/.test(i.hint) || /^[A-Z]/.test(i.hint)),
    treeData.items.filter((i: any) => !i.hint).map((i: any) => i.rel).join(",")
  );

  const heads = await call("tools/call", {
    name: "kb_heads",
    arguments: { page: "infohub/collector/l1-primitives" }
  });
  const headsData = JSON.parse(textOf(heads));
  check("kb_heads 返回标题", Array.isArray(headsData.headings) && headsData.headings.length > 0);
  check(
    "标题为英文",
    headsData.headings.every((h: any) => !/[\u4e00-\u9fff]/.test(h.title)),
    JSON.stringify(headsData.headings.slice(0, 2))
  );

  const sec = await call("tools/call", {
    name: "kb_read",
    arguments: { page: "infohub/collector/l1-primitives", section: "paging" }
  });
  const secData = JSON.parse(textOf(sec));
  check("kb_read --section 只回一节", String(secData.content).includes("软 404"));
  check("kb_read 不返回整页", !String(secData.content).includes("限速按 host"));

  const where = await call("tools/call", {
    name: "kb_where",
    arguments: { path: "collector/kit/paging.py" }
  });
  const whereData = JSON.parse(textOf(where));
  check("kb_where 命中采集页", whereData.hits.length >= 2, `hits=${whereData.hits.length}`);

  const miss = await call("tools/call", {
    name: "kb_where",
    arguments: { path: "collector/no-such-file.py" }
  });
  // 注意：architecture 页 covers 了 `collector/`，前缀匹配会命中它——这是设计行为，
  // 目录级 covers 的意义就是「这个目录下的一切都归它管」。
  check("kb_where 目录级 covers 前缀命中", JSON.parse(textOf(miss)).hits.length === 1);

  // 目录级 covers 是有意为之：infohub/overview 写了 covers: src/，
  // 所以 src/ 下任何路径都会命中它。真正「从未被任何页覆盖」的路径要用仓库外的形状。
  const miss2 = await call("tools/call", {
    name: "kb_where",
    arguments: { path: "zzz-uncovered-area/none.py" }
  });
  check("kb_where 完全未覆盖时返回空", JSON.parse(textOf(miss2)).hits.length === 0);

  // 跨仓库归属：本仓库（codeb）与 infohub 的路径不能互相串。
  // 曾经把 codeb 自己的 mcp-tools 页错放进 infohub/collector/，导致 where 串仓。
  const codebHit = await call("tools/call", {
    name: "kb_where",
    arguments: { path: "mcp/server.ts" }
  });
  const codebHits = JSON.parse(textOf(codebHit)).hits as Array<{ rel: string }>;
  check(
    "codeb 自身路径只归属 codeb/",
    codebHits.length > 0 && codebHits.every((h) => h.rel.startsWith("codeb/")),
    codebHits.map((h) => h.rel).join(",")
  );

  const infohubHit = await call("tools/call", {
    name: "kb_where",
    arguments: { path: "collector/kit/paging.py" }
  });
  const infohubHits = JSON.parse(textOf(infohubHit)).hits as Array<{ rel: string }>;
  check(
    "infohub 路径只归属 infohub/",
    infohubHits.length > 0 && infohubHits.every((h) => h.rel.startsWith("infohub/")),
    infohubHits.map((h) => h.rel).join(",")
  );

  const search = await call("tools/call", {
    name: "kb_search",
    arguments: { term: "软404" }
  });
  const searchData = JSON.parse(textOf(search));
  check("kb_search 空白不敏感", searchData.hits.length > 0, `hits=${searchData.hits.length}`);

  // 写入：先建、再更新、然后清理
  const tmpRel = "_shared/smoke-test";
  const created = await call("tools/call", {
    name: "kb_upsert",
    arguments: {
      page: tmpRel,
      repo: "_shared",
      title: "冒烟测试页",
      body: "## 用途\n\n仅用于验证 MCP 写入链路。",
      covers: ["mcp/server.ts"]
    }
  });
  const createdData = JSON.parse(textOf(created));
  check("kb_upsert 新建成功", createdData.action === "created", createdData.action);

  const appended = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, append: true, body: "## 追加节\n\n验证追加。" }
  });
  check("kb_upsert 追加成功", JSON.parse(textOf(appended)).action === "appended");

  const replaced = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, section: "用途", body: "仅用于验证 MCP 写入链路（已更新）。" }
  });
  check("kb_upsert 替换节成功", JSON.parse(textOf(replaced)).action === "section-replaced");

  const reread = await call("tools/call", {
    name: "kb_read",
    arguments: { page: tmpRel, section: "追加节" }
  });
  check("新建的页可被读回", String(JSON.parse(textOf(reread)).content).includes("验证追加"));

  // bodyFile：长正文的写入方式
  const { writeFileSync } = await import("node:fs");
  const bodyPath = join(HERE, "_tmp_body.md");
  writeFileSync(bodyPath, "## 文件正文\n\n来自 bodyFile 的内容。", "utf-8");
  const viaFile = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, section: "文件正文", bodyFile: bodyPath }
  });
  check("kb_upsert 支持 bodyFile", JSON.parse(textOf(viaFile)).action === "section-appended");
  const fileRead = await call("tools/call", {
    name: "kb_read",
    arguments: { page: tmpRel, section: "文件正文" }
  });
  check("bodyFile 内容已写入", String(JSON.parse(textOf(fileRead)).content).includes("来自 bodyFile"));

  /* ---- 细粒度替换（--find / expect）---- */

  // 先造一段带可替换文本的内容，并同时存在第二个节，用来证明「其余内容原样保留」。
  await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, append: true, body: "## 细粒度\n\n这个文件 9999 行。\n还有一处 9999 行。" }
  });

  const findOk = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, find: "9999 行", expect: 2, body: "体量最大" }
  });
  const findOkData = JSON.parse(textOf(findOk));
  check("find 替换命中两处", String(findOkData.action).includes("replaced-text"), findOkData.action);

  const afterFind = await call("tools/call", {
    name: "kb_read",
    arguments: { page: tmpRel, section: "细粒度" }
  });
  const afterFindText = String(JSON.parse(textOf(afterFind)).content);
  check("find 替换后旧文本消失", !afterFindText.includes("9999 行"));
  check("find 替换后新文本就位", afterFindText.includes("体量最大"));
  check("find 未破坏同节其他行", afterFindText.includes("还有一处"));

  // 命中数与 expect 不符 -> 中止且不写入
  const findMismatch = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, find: "体量最大", expect: 99, body: "不该写进去" }
  });
  check("find 命中数与 expect 不符时 isError", findMismatch?.isError === true);
  const afterMismatch = await call("tools/call", {
    name: "kb_read",
    arguments: { page: tmpRel, section: "细粒度" }
  });
  check(
    "find 中止后文件未改动",
    !String(JSON.parse(textOf(afterMismatch)).content).includes("不该写进去")
  );

  // find 不到 -> isError；find 缺替换值 -> isError
  const findMissing = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, find: "这段文本根本不存在xyz", body: "x" }
  });
  check("find 不到文本时 isError", findMissing?.isError === true);

  const findNoBody = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, find: "体量最大" }
  });
  check("find 缺替换值时 isError", findNoBody?.isError === true);

  // 空串 body = 删除命中文本
  // find 是字面匹配：空格、换行都必须与原文逐字符一致（文末行没有结尾换行）。
  const findDelete = await call("tools/call", {
    name: "kb_upsert",
    arguments: { page: tmpRel, find: "还有一处 体量最大。", body: "" }
  });
  const findDeleteData = JSON.parse(textOf(findDelete));
  check("find 空值删除成功", String(findDeleteData.action).includes("replaced-text"), findDeleteData.action);
  const afterDelete = await call("tools/call", {
    name: "kb_read",
    arguments: { page: tmpRel, section: "细粒度" }
  });
  const afterDeleteText = String(JSON.parse(textOf(afterDelete)).content);
  check("find 空值确实删掉了文本", !afterDeleteText.includes("还有一处"));
  check("find 删除未波及小节标题", afterDeleteText.includes("## 细粒度"));

  // ---------------- kb_pack / kb_dispatch 回归 ----------------
  //
  // 这两个命令的产物是「给 agent 读的册子」，所以断言落在**它自称的数据**上，
  // 而不是落在某段文案上：一旦装订规则改了，token 数、精度、块归属都会变，
  // 断言就会失败——这正是我们要的，不能让装订悄悄退化成「把整库塞进去」。

  const packDir = await call("tools/call", {
    name: "kb_pack",
    arguments: { scope: "collector/sites/", budget: 13000 }
  });
  const packDirData = JSON.parse(textOf(packDir));
  check("kb_pack 目录装订成功", packDirData.scope === "collector/sites", packDirData.scope);
  check("kb_pack 定位到正确仓库", packDirData.repo === "infohub", packDirData.repo);
  check(
    "kb_pack 自报精度 exact",
    packDirData.precision === "exact",
    packDirData.precision
  );
  check(
    "kb_pack 不超过预算",
    packDirData.total <= 13000,
    `total=${packDirData.total}`
  );
  check(
    "kb_pack 装进了交付物本身（sites 下的 YAML）",
    (packDirData.blocks ?? []).some(
      (b: any) => String(b.label).includes("announcement_list.yaml") && String(b.label).includes("全文")
    ),
    JSON.stringify((packDirData.blocks ?? []).map((b: any) => b.label).slice(0, 6))
  );
  check(
    "kb_pack 装进了检查清单（新站点必读）",
    (packDirData.blocks ?? []).some((b: any) => String(b.label).includes("检查清单")),
    JSON.stringify((packDirData.blocks ?? []).map((b: any) => b.label))
  );

  // 大文件必须退大纲：kb.py 1432 行 / 17k tok，全文塞不进 13k 预算。
  const packBig = await call("tools/call", {
    name: "kb_pack",
    arguments: { scope: "kb.py" }
  });
  const packBigData = JSON.parse(textOf(packBig));
  check("kb_pack 超长文件退大纲", packBigData.total < 13000, `total=${packBigData.total}`);
  check(
    "kb_pack 大纲块声明为大纲",
    (packBigData.blocks ?? []).some(
      (b: any) => String(b.label).startsWith("kb.py") && String(b.label).includes("大纲")
    ),
    JSON.stringify((packBigData.blocks ?? []).map((b: any) => b.label).slice(0, 4))
  );

  // 预算压到极低时，知识层会被挤光。这时必须**明说**，
  // 否则 agent 会照着源码开工，却不知道那些「改了会静默出错」的约束。
  const packTiny = await call("tools/call", {
    name: "kb_pack",
    arguments: { scope: "collector/kit/", budget: 1200 }
  });
  const packTinyData = JSON.parse(textOf(packTiny));
  check(
    "kb_pack 预算不足时标记 knowledge_lost",
    packTinyData.knowledge_lost === true,
    `total=${packTinyData.total} lost=${packTinyData.knowledge_lost}`
  );
  check(
    "kb_pack 预算不足时仍有源码",
    (packTinyData.blocks ?? []).length > 0,
    `blocks=${(packTinyData.blocks ?? []).length}`
  );

  // 定位不到的 scope 必须报错，不能安静返回一个空册子。
  let packMissingErrored = false;
  try {
    const bad = await call("tools/call", {
      name: "kb_pack",
      arguments: { scope: "collector/definitely-not-here/" }
    });
    packMissingErrored = bad?.isError === true;
  } catch {
    packMissingErrored = true;
  }
  check("kb_pack 定位不到时报错", packMissingErrored);

  const disp = await call("tools/call", {
    name: "kb_dispatch",
    arguments: { scopes: ["collector/kit/", "collector/refs/", "collector/site_crawl/"] }
  });
  const dispData = JSON.parse(textOf(disp));
  check("kb_dispatch 三个范围零冲突", (dispData.conflicts ?? []).length === 0,
    JSON.stringify(dispData.conflicts));
  check(
    "kb_dispatch 找出共享知识页",
    Object.keys(dispData.shared_pages ?? {}).includes("infohub/collector/architecture"),
    JSON.stringify(Object.keys(dispData.shared_pages ?? {}))
  );

  // 重叠范围必须报冲突。这是并行派发唯一的硬闸：漏报就是两个 agent 互相覆盖。
  const dispBad = await call("tools/call", {
    name: "kb_dispatch",
    arguments: { scopes: ["collector/", "collector/kit/"] }
  });
  const dispBadData = JSON.parse(textOf(dispBad));
  check("kb_dispatch 识别嵌套范围冲突", (dispBadData.conflicts ?? []).length > 0,
    JSON.stringify(dispBadData.conflicts));

  // 写范围之外的派生物：collector/sites 里只有 YAML，
  // 但改完必须重跑 capabilities.py 生成 capabilities.json。
  // 这条发现不了，两个并行任务各加一个站点时，先加的会静默消失。
  const dispSites = await call("tools/call", {
    name: "kb_dispatch",
    arguments: { scopes: ["collector/sites/"] }
  });
  const dispSitesData = JSON.parse(textOf(dispSites));
  const sitesOut = (dispSitesData.scopes?.[0]?.derived_out ?? []).map((d: any) => d.file);
  check(
    "kb_dispatch 报出写范围外的派生文件",
    sitesOut.some((f: string) => f.includes("capabilities.json")),
    JSON.stringify(sitesOut)
  );
  check(
    "kb_dispatch 派生文件带生成器标记",
    (dispSitesData.scopes?.[0]?.derived_out ?? []).some(
      (d: any) => String(d.mark).includes("capabilities.py")
    ),
    JSON.stringify(dispSitesData.scopes?.[0]?.derived_out)
  );

  // 同一个派生物被多个范围命中时，必须从「每张卡各自提醒」升级为全局串行点。
  // 否则 7 个 agent 各跑一次生成器，最后只剩一个人的结果。
  const dispAll = await call("tools/call", {
    name: "kb_dispatch",
    arguments: { scopes: ["collector/kit/", "collector/refs/", "collector/sites/"] }
  });
  const dispAllData = JSON.parse(textOf(dispAll));
  const hot = dispAllData.serial_bottlenecks ?? {};
  check(
    "kb_dispatch 多范围共碰同一派生物时升级为全局串行点",
    Object.keys(hot).some((k) => k.includes("capabilities.json")),
    JSON.stringify(hot)
  );
  check(
    "kb_dispatch 全局串行点列出全部相关范围",
    Object.values(hot).some((v: any) => Array.isArray(v) && v.length >= 3),
    JSON.stringify(hot)
  );

  // ---------------- --repo 校验：静默失败高发处 ----------------
  //
  // 这三个命令都会静默过滤掉不存在的仓库，然后给出一个**看起来正常**的空结果：
  //   tree   -> 「0 页」          模型以为仓库是空的
  //   where  -> 「没有页面覆盖」   模型以为无人认领，于是新建重复页
  //   search -> 「没有命中」
  // 后两个尤其危险：空结果本身是合法答案，前提只是仓库名拼对了。
  // 实测一个判断类任务因此白烧 4 轮（模型反复换工具重试）。
  for (const cmd of ["tree", "where", "search"]) {
    const args: any = { name: "tree", arguments: { repo: "collector/kit" } };
    if (cmd === "where") args.name = "kb_where", args.arguments = { path: "x.py", repo: "nope" };
    if (cmd === "search") args.name = "kb_search", args.arguments = { term: "kb", repo: "nope" };
    if (cmd === "tree") args.arguments = { repo: "collector/kit" };
    let errored = false;
    let said = "";
    try {
      const r = await call("tools/call", args);
      errored = r?.isError === true;
      said = textOf(r);
    } catch (e: any) {
      errored = true;
      said = String(e?.message ?? e);
    }
    check(`kb_${cmd} 拒绝不存在的仓库名`, errored, said.slice(0, 120));
    check(`kb_${cmd} 错误里列出可用仓库`, said.includes("infohub"), said.slice(0, 120));
  }

  // 「改 X 有哪些坑」是最高频的提问，而它的答案不在源码里。
  // 实测单文件 pack：6968 tok（源码占 5204 = 75%）→ noSource 后 1764 tok。
  const packNoSrc = await call("tools/call", {
    name: "kb_pack",
    arguments: { scope: "collector/kit/paging.py", noSource: true }
  });
  const packNoSrcData = JSON.parse(textOf(packNoSrc));
  const packFull = JSON.parse(textOf(await call("tools/call", {
    name: "kb_pack", arguments: { scope: "collector/kit/paging.py" }
  })));
  check(
    "kb_pack noSource 省掉源码块",
    !(packNoSrcData.blocks ?? []).some((b: any) => b.prio >= 4),
    JSON.stringify((packNoSrcData.blocks ?? []).map((b: any) => b.prio))
  );
  check(
    "kb_pack noSource 保留知识块",
    (packNoSrcData.blocks ?? []).some((b: any) => b.prio === 3),
    JSON.stringify((packNoSrcData.blocks ?? []).map((b: any) => b.label))
  );
  check(
    "kb_pack noSource 至少省一半",
    packNoSrcData.total < packFull.total * 0.5,
    `noSource=${packNoSrcData.total} full=${packFull.total}`
  );

  // 「某目录下有哪些文件」必须给出文件清单，否则 agent 只能反复重试。
  // 实测 dispatch 原先只说「6 个代码文件」而不列出，导致同一调用重复 3 次。
  const dispText = textOf(await call("tools/call", {
    name: "kb_dispatch", arguments: { scopes: ["collector/kit/"] }
  }));
  check("kb_dispatch 列出写范围内的具体文件", dispText.includes("collector/kit/paging.py"),
    dispText.slice(0, 200));

  // ---------------- kb_route 回归 ----------------
  //
  // 三条不变式，每条都对应一次实测出来的失败：
  //  1. 带仓库前缀的路径 == 裸路径（前缀那个 bug 会装出 0 块 0 tok 且 rc=0）
  //  2. 成员清单永不丢（压预算时不能把大文件整块删掉）
  //  3. 超预算默认拒绝（悄悄降档 = 答案基于大纲，而它看着像成功）

  const bareDir = await call("tools/call", {
    name: "kb_pack", arguments: { scope: "apps/web/src/components/ui/", budget: 13000 }
  });
  const bareDirData = JSON.parse(textOf(bareDir));

  // 1. 提议器
  const around = await call("tools/call", {
    name: "kb_route",
    arguments: { around: "atomkgraph/apps/web/src/components/Sidebar.tsx", depth: 1 }
  });
  const aroundData = JSON.parse(textOf(around));
  check("kb_route around 找到 import 闭包", (aroundData.members ?? []).length >= 2,
    `members=${(aroundData.members ?? []).length}`);
  check("kb_route around 包含 api.ts（1-hop 里最大的那个）",
    (aroundData.members ?? []).some((m: any) => m.path.endsWith("api.ts")),
    JSON.stringify((aroundData.members ?? []).map((m: any) => m.path)));
  check("kb_route around 给出建议 role",
    (aroundData.members ?? []).every((m: any) =>
      ["full", "index", "outline"].includes(m.suggest)),
    JSON.stringify((aroundData.members ?? []).map((m: any) => m.suggest)));
  check("kb_route around 把最大的文件建议成非 full",
    (aroundData.members ?? [])
      .filter((m: any) => m.tokens > 6000)
      .every((m: any) => m.suggest !== "full"),
    "大于 6000 tok 的文件不该建议 full");

  // 2. 装订 + 每成员保真度真的生效
  const specPath = join(HERE, "_tmp_route_smoke.json");
  const { writeFileSync: writeSpec } = await import("node:fs");
  writeSpec(specPath, JSON.stringify({
    repo: "atomkgraph",
    entry: "apps/web/src/components/Sidebar.tsx",
    budget: 200000,
    members: [
      { path: "apps/web/src/components/Sidebar.tsx", role: "full", why: "落点" },
      { path: "apps/web/src/lib/utils.ts", role: "full" },
      { path: "apps/web/src/api.ts", role: "index" }
    ],
    questions: ["这个组件依赖哪些模块？"]
  }, null, 2), "utf-8");

  const routed = await call("tools/call", {
    name: "kb_route", arguments: { specPath }
  });
  const routedData = JSON.parse(textOf(routed));
  check("kb_route 成员数等于规格", (routedData.members ?? []).length === 3,
    JSON.stringify((routedData.members ?? []).map((m: any) => m.path)));
  check("kb_route full 成员装进了原文",
    (routedData.blocks ?? []).some(
      (b: any) => String(b.label).includes("Sidebar.tsx") &&
                  String(b.label).includes("全文") &&
                  String(b.text).includes("export function")),
    JSON.stringify((routedData.blocks ?? []).map((b: any) => b.label)));
  check("kb_route index 成员只给索引、不给正文",
    (routedData.blocks ?? []).some(
      (b: any) => String(b.label).includes("api.ts") &&
                  String(b.label).includes("语义块索引")) &&
    !(routedData.blocks ?? []).some(
      (b: any) => String(b.label).includes("api.ts") && String(b.label).includes("全文")),
    JSON.stringify((routedData.blocks ?? []).map((b: any) => b.label)));
  check("kb_route 把 questions 带进包",
    String(textOf(routed)).includes("这个组件依赖哪些模块？"));

  // 3. 不变式：压预算 + degrade，成员一个都不能少
  //
  // 2,000 tok 是个「降档能救」的量级：Sidebar 5383 全文 → 746 索引，
  // utils 78 全文保留，api.ts 本来就是索引。降到 800 就救不回来了——
  // 全部 outline 也要 1804，那是任务太大该拆，不该假装装得下。
  const squeezed = await call("tools/call", {
    name: "kb_route", arguments: { specPath, budget: 2000, degrade: true }
  });
  const squeezedData = JSON.parse(textOf(squeezed));
  check("kb_route 降档后成员清单一个不少",
    (squeezedData.members ?? []).length === 3,
    `members=${(squeezedData.members ?? []).length}`);
  check("kb_route 降档后确实降了档",
    (squeezedData.degraded ?? []).length > 0,
    JSON.stringify(squeezedData.degraded));
  check("kb_route 降档后不超预算",
    squeezedData.total <= 2000, `total=${squeezedData.total}`);
  check("kb_route 降档记录写明省了多少",
    (squeezedData.degraded ?? []).every((x: any) => typeof x.saved === "number" && x.saved > 0),
    JSON.stringify(squeezedData.degraded));

  // 3b. 降到底仍超预算 → 必须报错，不能输出超预算的包
  let tooSmallRejected = false;
  let tooSmallMsg = "";
  try {
    const r = await call("tools/call", {
      name: "kb_route", arguments: { specPath, budget: 800, degrade: true }
    });
    tooSmallMsg = textOf(r);
    tooSmallRejected = r?.isError === true;
  } catch (e: any) {
    tooSmallMsg = String(e?.message ?? e);
    tooSmallRejected = true;
  }
  check("kb_route 降到底仍超预算时报错而不是硬塞", tooSmallRejected,
    tooSmallMsg.slice(0, 150));
  check("kb_route 此时给出「预算至少要给到多少」",
    tooSmallMsg.includes("预算至少要给到"), tooSmallMsg.slice(0, 200));

  // 4. 超预算默认拒绝（非零退出 → MCP 层是 isError）
  let overBudgetRejected = false;
  let overBudgetMsg = "";
  try {
    const r = await call("tools/call", {
      name: "kb_route", arguments: { specPath, budget: 800 }
    });
    overBudgetMsg = textOf(r);
    overBudgetRejected = r?.isError === true;
  } catch (e: any) {
    overBudgetMsg = String(e?.message ?? e);
    overBudgetRejected = true;
  }
  check("kb_route 超预算默认拒绝装订", overBudgetRejected, overBudgetMsg.slice(0, 150));
  check("kb_route 拒绝时给出每个成员的 tok 明细",
    overBudgetMsg.includes("--degrade") && overBudgetMsg.includes("tok"),
    overBudgetMsg.slice(0, 200));

  // 5. 前缀归一：带仓库前缀与裸路径必须装出同样的东西
  const prefixed = await call("tools/call", {
    name: "kb_pack", arguments: { scope: "atomkgraph/apps/web/src/components/ui/", budget: 13000 }
  });
  const prefixedData = JSON.parse(textOf(prefixed));
  check("kb_pack 带仓库前缀的目录能装出内容（曾恒为 0）",
    prefixedData.total > 0, `total=${prefixedData.total}`);
  check("kb_pack 带前缀与裸路径装订量一致",
    prefixedData.total === bareDirData.total,
    `prefixed=${prefixedData.total} bare=${bareDirData.total}`);
  check("kb_pack 带前缀与裸路径块数一致",
    (prefixedData.blocks ?? []).length === (bareDirData.blocks ?? []).length,
    `prefixed=${(prefixedData.blocks ?? []).length} bare=${(bareDirData.blocks ?? []).length}`);

  // 6. 单文件带前缀不许把落点文件当成自己的兄弟再装一遍
  //
  // 判据是「prio 有多块同文件」：落点本身是 prio 5，兄弟大纲是 prio 1。
  // 早先的 bug 就表现为同一个文件既有 prio 5 全文、又有 prio 1 大纲（多付 43 tok）。
  const onePrefixed = await call("tools/call", {
    name: "kb_pack",
    arguments: { scope: "atomkgraph/apps/web/src/components/ui/button.tsx", budget: 13000 }
  });
  const onePrefixedData = JSON.parse(textOf(onePrefixed));
  const selfBlocks = (onePrefixedData.blocks ?? []).filter(
    (b: any) => String(b.label).startsWith("apps/web/src/components/ui/button.tsx"));
  check("kb_pack 单文件带前缀只装一块自己（不重复成兄弟大纲）",
    selfBlocks.length === 1,
    JSON.stringify(selfBlocks.map((b: any) => `prio${b.prio} ${b.label}`)));
  check("kb_pack 那一块是 prio 5 全文（不是被降级成兄弟大纲）",
    selfBlocks.length === 1 && selfBlocks[0].prio === 5,
    JSON.stringify(selfBlocks.map((b: any) => `prio${b.prio}`)));

  // 7. 选型规则的唯一来源是 git，不再有 .kbignore 这第二份清单。
  //
  // 实测出来的冲突：webview/ 的 8 个文件都已进 git，却被 repo/.kbignore
  // 写成「不是源码」。dispatch 报「写范围 0 个代码文件」，而 route --around
  // 又能看见它们——两条路径对同一批文件给出相反结论，正是双真值的代价。
  const dispWeb = textOf(await call("tools/call", {
    name: "kb_dispatch", arguments: { scopes: ["webview/"] }
  }));
  check("kb_dispatch 看得见 git 已跟踪的 webview 源码",
    dispWeb.includes("webview/server.mjs") && dispWeb.includes("webview/data.mjs"),
    dispWeb.slice(0, 220));
  check("kb_dispatch 的 webview 写范围不是 0 个文件",
    !dispWeb.includes("写范围 0 个代码文件"), dispWeb.slice(0, 220));

  const packWeb = JSON.parse(textOf(await call("tools/call", {
    name: "kb_pack", arguments: { scope: "webview/", budget: 20000 }
  })));
  check("kb_pack 装出了 webview 的源码（不再是 0 块）",
    packWeb.total > 0 && (packWeb.blocks ?? []).some(
      (b: any) => String(b.label).includes("webview/")),
    `total=${packWeb.total} blocks=${(packWeb.blocks ?? []).length}`);

  const aroundWeb = JSON.parse(textOf(await call("tools/call", {
    name: "kb_route", arguments: { around: "webview/server.mjs", depth: 1 }
  })));
  check("kb_route around 解析出 .mjs 相对 import（server→data/sqlite）",
    (aroundWeb.members ?? []).some((m: any) => m.path === "webview/data.mjs") &&
    (aroundWeb.members ?? []).some((m: any) => m.path === "webview/sqlite.mjs"),
    JSON.stringify((aroundWeb.members ?? []).map((m: any) => m.path)));

  // 冒烟测试自己创建的文件自己删。否则每跑一次就留一个 _tmp_route_smoke.json，
  // 而它写的路径是绝对路径，别人 clone 仓库后第一次跑就会看到「未跟踪文件」。
  const { unlinkSync } = await import("node:fs");
  try { unlinkSync(specPath); } catch { /* 已被删掉也无所谓 */ }

  // 模型分不清「代码路径」和「知识页路径」：它会 read 一个 .py。
  // 只说「不存在」它不会想到换工具（实测绕两圈），必须指出该用哪条命令。
  let readCodeErr = "";
  try {
    const r = await call("tools/call", {
      name: "kb_read", arguments: { page: "collector/kit/paging.py" }
    });
    readCodeErr = textOf(r);
    check("kb_read 拒绝代码路径", r?.isError === true, readCodeErr.slice(0, 100));
  } catch (e: any) {
    readCodeErr = String(e?.message ?? e);
    check("kb_read 拒绝代码路径", true);
  }
  check("kb_read 代码路径错误里给出 kb_pack", readCodeErr.includes("kb pack"),
    readCodeErr.slice(0, 160));

  const err = await call("tools/call", { name: "kb_read", arguments: { page: "不存在的页" } });
  check("读不存在的页标记 isError", err?.isError === true);

  // MCP 规范：未知工具属于协议级错误，返回 JSON-RPC error 而非 isError result
  let unknownErrored = false;
  try {
    await call("tools/call", { name: "kb_nope", arguments: {} });
  } catch {
    unknownErrored = true;
  }
  check("未知工具返回 JSON-RPC error", unknownErrored);

  // 清理
  const { rmSync } = await import("node:fs");
  for (const f of [
    join(HERE, "..", "repo", "_shared", "smoke-test.md"),
    bodyPath
  ]) {
    try {
      rmSync(f);
    } catch {
      /* ignore */
    }
  }

  console.log(`\n${passed} 通过 / ${failed} 失败`);
  if (failed > 0 && stderr) console.log("\nserver stderr:\n" + stderr.slice(0, 800));
  child.kill();
  process.exit(failed === 0 ? 0 : 1);
}

main().catch((err) => {
  console.error("测试异常：", err);
  if (stderr) console.error(stderr.slice(0, 800));
  child.kill();
  process.exit(1);
});
