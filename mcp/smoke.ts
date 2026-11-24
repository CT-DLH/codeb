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
  check("tools/list 返回 8 个工具", names.length === 8, `实际 ${names.length}: ${names}`);
  for (const want of ["kb_tree", "kb_read", "kb_heads", "kb_search", "kb_where",
                      "kb_pack", "kb_dispatch", "kb_upsert"]) {
    check(`工具有 ${want}`, names.includes(want));
  }

  const tree = await call("tools/call", { name: "kb_tree", arguments: {} });
  const treeData = JSON.parse(textOf(tree));
  check("kb_tree 有页面", treeData.stats.pages > 0, `pages=${treeData.stats.pages}`);
  check("kb_tree 按目录折叠", treeData.items[0].rel.includes("/"));

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
    const args: any = { name: "kb_tree", arguments: { repo: "collector/kit" } };
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
