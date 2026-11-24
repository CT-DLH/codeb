/**
 * 打印 MCP 客户端实际会看到的握手结果与工具清单。
 * 用途：把 server.ts 注册的工具与 .mcp.json 配置对齐检查，并给出一段可直接粘贴的调用示例。
 *
 * 用法：node mcp/inspect.ts
 */
import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

interface Pending {
  resolve: (v: any) => void;
  reject: (e: Error) => void;
}

const child = spawn(process.execPath, [join(HERE, "server.ts")], {
  stdio: ["pipe", "pipe", "pipe"],
  windowsHide: true
});

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
    const msg = JSON.parse(line);
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
    }, 15000);
  });
}

async function main(): Promise<void> {
  console.log("=== .mcp.json 配置 ===");
  const cfg = JSON.parse(readFileSync(join(HERE, "..", ".mcp.json"), "utf-8"));
  console.log(JSON.stringify(cfg, null, 2));

  const init = await call("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "inspect", version: "1" }
  });
  child.stdin.write(
    JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n"
  );

  console.log("\n=== 握手 ===");
  console.log(`server   : ${init.serverInfo.name} ${init.serverInfo.version}`);
  console.log(`protocol : ${init.protocolVersion}`);
  console.log(`tools    : ${JSON.stringify(init.capabilities.tools)}`);

  const list = await call("tools/list");
  console.log(`\n=== ${list.tools.length} 个工具 ===`);
  for (const t of list.tools) {
    const req: string[] = t.inputSchema?.required ?? [];
    const props = Object.keys(t.inputSchema?.properties ?? {});
    console.log(`\n${t.name}`);
    console.log(`  参数: ${props.map((p) => (req.includes(p) ? p + "*" : p)).join(", ") || "(无)"}`);
    console.log(`  说明: ${String(t.description).split("\n")[0]}`);
  }

  console.log("\n=== 一次完整写入调用的原文（可直接粘贴给客户端）===");
  console.log(
    JSON.stringify(
      {
        jsonrpc: "2.0",
        id: 1,
        method: "tools/call",
        params: {
          name: "kb_upsert",
          arguments: {
            repo: "infohub",
            topic: "collector",
            title: "Some new topic",
            covers: ["collector/kit/"],
            body: "## What\n\n正文。"
          }
        }
      },
      null,
      2
    )
  );

  child.kill();
}

main().catch((e) => {
  console.error("失败：", e);
  child.kill();
  process.exit(1);
});
