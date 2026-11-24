/**
 * 决定性验证：pi-agent-core 能不能接我们现有的 NVIDIA 端点，并且把 codeb 的
 * 工具当 in-process 函数调用（不起 subprocess、不重写工具定义）。
 *
 * 只装两个包试，不装 pi-coding-agent（11 MB，我们不需要它的 CLI / TUI）。
 */
import { Agent } from "@mariozechner/pi-agent-core";
import { Type } from "typebox";
import { spawn } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";

// 凭据不在环境变量里，在 infohub 的 .env 中（与 distill.py 同一真源）
function loadEnv() {
  const out = {};
  const p = "D:/work/project/infohub/collector/.env";
  if (!existsSync(p)) return out;
  for (const line of readFileSync(p, "utf-8").split(/\r?\n/)) {
    const s = line.trim();
    if (!s || s.startsWith("#") || !s.includes("=")) continue;
    const [k, ...rest] = s.split("=");
    if (k.trim().startsWith("ZHIHU_LLM_")) {
      out[k.trim()] = rest.join("=").trim().replace(/^["']|["']$/g, "");
    }
  }
  return out;
}
const ENV = loadEnv();

const BASE = process.env.ZHIHU_LLM_BASE_URL || ENV.ZHIHU_LLM_BASE_URL
  || "https://integrate.api.nvidia.com/v1";
const MODEL = process.env.ZHIHU_LLM_MODEL || ENV.ZHIHU_LLM_MODEL
  || "nvidia/nemotron-3.5-lightning-30b-a3b";
const KEY = process.env.ZHIHU_LLM_API_KEY || ENV.ZHIHU_LLM_API_KEY || "";

// 手工构造 Model：pi 的自带 registry 里没有 NVIDIA，我们要的正是这个能力
const model = {
  id: MODEL,
  name: "nemotron via nvidia",
  api: "openai-completions",
  provider: "nvidia",
  baseUrl: BASE,
  reasoning: true,
  input: ["text"],
  cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
  contextWindow: 128000,
  maxTokens: 4096,
  compat: {
    supportsDeveloperRole: false,
    supportsReasoningEffort: false,
  },
};

/* ---- 把 codeb 的 kb.py 包成一个 in-process 工具 ----
 *
 * 关键决定：**不**走 MCP、**不**spawn 每次调用。
 * 实测 in-process 54ms vs subprocess 261ms；而且工具定义不用重写一遍。
 * 这里仍然 spawn 一次 python 进程，但那是因为 kb.py 是 Python —— 换成本地
 * 起到长期驻留的子进程（下一版）即可，语义不变。
 */
function kbTool(name, label, description, paramSchema, buildArgs) {
  return {
    name,
    label,
    description,
    parameters: paramSchema,
    execute: async (toolCallId, params, signal) => {
      const args = buildArgs(params);
      const t0 = Date.now();
      const r = await new Promise((resolve) => {
        const p = spawn("python", ["-X", "utf8", "kb.py", ...args, "--json"], {
          cwd: "D:/work/project/codeb",
          windowsHide: true,
        });
        let out = "", err = "";
        p.stdout.on("data", (d) => (out += d));
        p.stderr.on("data", (d) => (err += d));
        p.on("close", (code) => resolve({ code, out, err }));
      });
      const ms = Date.now() - t0;
      if (r.code !== 0) throw new Error(r.err || `kb 退出码 ${r.code}`);
      return {
        content: [{ type: "text", text: r.out.trim() }],
        details: { ms, bytes: r.out.length },
      };
    },
  };
}

const tools = [
  kbTool("kb_tree", "知识库导航", "按目录折叠列出全部页面标题，会话开始时先调。",
    Type.Object({ repo: Type.Optional(Type.String()) }),
    (p) => (p.repo ? ["tree", "--repo", p.repo] : ["tree"])),
  kbTool("kb_pack", "装订上下文", "为一个代码范围装订上下文册子：源码 + 相关节 + 计划。",
    Type.Object({ scope: Type.String(), budget: Type.Optional(Type.Number()) }),
    (p) => (p.budget ? ["pack", p.scope, "--budget", String(p.budget)] : ["pack", p.scope])),
  kbTool("kb_dispatch", "派发检查", "检查多个写范围能否并行。",
    Type.Object({ scopes: Type.Array(Type.String()) }),
    (p) => ["dispatch", ...p.scopes]),
];

console.log("=== pi-agent-core 接 NVIDIA 实测 ===");
console.log(`model: ${MODEL}`);
console.log(`base:  ${BASE}`);
console.log(`tools: ${tools.map((t) => t.name).join(", ")}`);
console.log();

const agent = new Agent({
  initialState: {
    systemPrompt: "你是代码知识库助手。回答简短，用中文。需要知识库内容时调用工具。",
    model,
    thinkingLevel: "off",
    tools,
    messages: [],
  },
  getApiKey: () => KEY,
});

let sawTool = false;
agent.subscribe((ev) => {
  if (ev.type === "tool_execution_start") {
    sawTool = true;
    console.log(`  [tool] ${ev.toolName}(${JSON.stringify(ev.args).slice(0, 80)})`);
  }
  if (ev.type === "tool_execution_end") {
    console.log(`  [done] ${ev.toolName} isError=${ev.isError} ` +
                `${JSON.stringify(ev.result?.details ?? {}).slice(0, 60)}`);
  }
  if (ev.type === "message_end") {
    // pi 的约定：失败编码在 message 里，不抛异常。必须显式检查。
    const m = ev.message;
    if (m?.stopReason === "error" || m?.errorMessage) {
      console.log(`  [ERROR] stopReason=${m.stopReason} msg=${m.errorMessage}`);
    }
  }
  if (ev.type === "message_update" && ev.assistantMessageEvent?.type === "text_delta") {
    process.stdout.write(ev.assistantMessageEvent.delta ?? "");
  }
});

const t0 = Date.now();
await agent.prompt("用一句话告诉我这个知识库有几个仓库，然后列出 infohub 仓库下的页面数。");
await agent.waitForIdle();
console.log();
console.log(`\n耗时 ${Date.now() - t0}ms，触发工具调用: ${sawTool}`);
