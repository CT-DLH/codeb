/**
 * codeb chat — 会话历史持久化（Node 22.5+ / 24 的 node:sqlite）。
 *
 * 为什么单独一个 db 文件：_kbwork/codeb-index.db 是 `kb reindex` 的**派生索引**，
 * 重建时整库可能被重写；会话历史是用户数据，不能跟着被冲掉。所以放
 * _kbwork/codeb-chat.db，与派生索引彻底隔离。
 *
 * 表：
 *   sessions  — 会话头（标题/仓库/模型/时间/是否 cot）
 *   messages  — 消息（role/text/tools/cot/error），一条一轮 assistant
 *
 * 设计取舍：
 * - **前端是写入方**：每一轮 done 后把整条 assistant 消息写进来；
 *   tool_call/tool_result 也一起存，恢复后轨迹页仍可看。
 * - **存展示数据，不存 LLM history**：reasoning 存下来仅供展示，
 *   真正的 LLM history（含 tool_call_id）由 chat_engine.restore_history 恢复时
 *   从前端传回的 llmHistory 重建。两者分开，避免把折叠账本混进来。
 */
import fs from 'node:fs'
import path from 'node:path'

let DatabaseSync = null
try {
  ;({ DatabaseSync } = await import('node:sqlite'))
} catch {
  // 老 Node 没有 sqlite：graceful degradation，聊天照常用，只是不落盘。
}

const SCHEMA = `
CREATE TABLE IF NOT EXISTS sessions (
  id          TEXT PRIMARY KEY,
  title       TEXT NOT NULL DEFAULT '',
  repo        TEXT NOT NULL DEFAULT 'codeb',
  model       TEXT NOT NULL DEFAULT '',
  cot         INTEGER NOT NULL DEFAULT 0,
  tree_depth  INTEGER NOT NULL DEFAULT 3,
  created_at  INTEGER NOT NULL,
  updated_at  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id  TEXT NOT NULL,
  seq         INTEGER NOT NULL,
  role        TEXT NOT NULL,
  text        TEXT NOT NULL DEFAULT '',
  cot         TEXT NOT NULL DEFAULT '',
  tools_json  TEXT NOT NULL DEFAULT '[]',
  llm_json    TEXT NOT NULL DEFAULT '[]',
  usage_json  TEXT NOT NULL DEFAULT '{}',
  error       TEXT NOT NULL DEFAULT '',
  stopped     INTEGER NOT NULL DEFAULT 0,
  created_at  INTEGER NOT NULL,
  UNIQUE(session_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_msg_session ON messages(session_id, seq);
`

export function chatDbPath(root) {
  return path.join(root, '_kbwork', 'codeb-chat.db')
}

function open(root) {
  if (!DatabaseSync) return null
  const dir = path.join(root, '_kbwork')
  try { fs.mkdirSync(dir, { recursive: true }) } catch { return null }
  try {
    const db = new DatabaseSync(chatDbPath(root))
    db.exec(SCHEMA)
    // CREATE TABLE IF NOT EXISTS 不给旧表补列：显式迁移。
    // 老库（本轮之前建的）没有 usage_json，不补的话 INSERT 会报 no such column。
    const cols = db.prepare('PRAGMA table_info(messages)').all().map((c) => c.name)
    if (!cols.includes('usage_json')) {
      db.exec("ALTER TABLE messages ADD COLUMN usage_json TEXT NOT NULL DEFAULT '{}'")
    }
    return db
  } catch {
    return null
  }
}

const now = () => Date.now()

/** 列出所有已保存会话（按最近更新倒序）。 */
export function listSessions(root) {
  const db = open(root)
  if (!db) return []
  try {
    return db.prepare(
      'SELECT id, title, repo, model, cot, tree_depth, created_at, updated_at '
      + 'FROM sessions ORDER BY updated_at DESC'
    ).all().map((r) => ({ ...r, cot: !!r.cot }))
  } catch {
    return []
  } finally {
    try { db.close() } catch { /* ignore */ }
  }
}

/** 读一个会话的全部消息（按 seq 正序）。 */
export function loadSession(root, id) {
  const db = open(root)
  if (!db) return null
  try {
    const s = db.prepare('SELECT * FROM sessions WHERE id = ?').get(id)
    if (!s) return null
    const msgs = db.prepare(
      'SELECT seq, role, text, cot, tools_json, llm_json, usage_json, error, stopped '
      + 'FROM messages WHERE session_id = ? ORDER BY seq'
    ).all(id).map((m) => ({
      seq: m.seq, role: m.role, text: m.text, cot: m.cot || '',
      tools: safeParse(m.tools_json, []),
      llm: safeParse(m.llm_json, []),
      usage: safeParse(m.usage_json, {}),
      error: m.error || '', stopped: !!m.stopped,
    }))
    return { session: { ...s, cot: !!s.cot }, messages: msgs }
  } catch {
    return null
  } finally {
    try { db.close() } catch { /* ignore */ }
  }
}

/**
 * 从某个会话的第 upToSeq 条消息（含）分叉出一个新会话。
 *
 * 关键：llmHistory 必须取**分叉点所在 assistant 那条**存的 LLM 消息，
 * 而不是整条会话最后一条——分支之后要接着它往下聊，
 * 用最后一条会把分支点之后的历史混进来，等于没分叉。
 * 若分叉点不是 assistant（比如点在 user 上），则往上找最近一条
 * assistant 的 llm；一条都没有就是空 history（新会话从头开始）。
 */
export function forkSession(root, srcId, upToSeq, newId, title) {
  const db = open(root)
  if (!db) return { ok: false, error: 'sqlite unavailable' }
  try {
    const src = db.prepare('SELECT * FROM sessions WHERE id = ?').get(srcId)
    if (!src) throw new Error('源会话不存在')
    const rows = db.prepare(
      'SELECT * FROM messages WHERE session_id = ? AND seq <= ? ORDER BY seq'
    ).all(srcId, Number(upToSeq))
    if (!rows.length) throw new Error('分叉点之前没有消息')

    // 往前找最近一条带 llm 的 assistant 消息作为恢复点。
    // 记索引而不是靠内容相等去匹配——两条消息可能有相同的 llm，
    // 那样会把 llm 挂到多处，恢复时语义就乱了。
    let llm = []
    let restoreIdx = -1
    for (let i = rows.length - 1; i >= 0; i--) {
      const r = rows[i]
      if (r.role !== 'assistant') continue
      const arr = safeParse(r.llm_json, [])
      if (arr.length) { llm = arr; restoreIdx = i; break }
    }

    const t = now()
    db.exec('BEGIN')
    db.prepare(
      'INSERT INTO sessions (id, title, repo, model, cot, tree_depth, created_at, updated_at) '
      + 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    ).run(
      newId, String(title || src.title + '（分支）'), src.repo, src.model,
      src.cot, src.tree_depth, t, t,
    )
    const ins = db.prepare(
      'INSERT INTO messages (session_id, seq, role, text, cot, tools_json, llm_json, '
      + 'usage_json, error, stopped, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    )
    for (let i = 0; i < rows.length; i++) {
      const r = rows[i]
      // 只把 llm 挂到恢复点那一条 assistant 上；其余清空，
      // 恢复时用 find(llm && llm.length) 取到的就是它。
      ins.run(
        newId, i, r.role, r.text, r.cot, r.tools_json,
        i === restoreIdx ? JSON.stringify(llm) : '[]',
        r.usage_json || '{}', r.error, r.stopped, t,
      )
    }
    db.exec('COMMIT')
    return { ok: true, id: newId, count: rows.length, restoredFromLlm: llm.length > 0 }
  } catch (e) {
    try { db.exec('ROLLBACK') } catch { /* ignore */ }
    return { ok: false, error: String(e?.message || e) }
  } finally {
    try { db.close() } catch { /* ignore */ }
  }
}

/**
 * 保存/覆盖一个会话。messages 里每条必须有 seq（前端数组下标）。
 * 用事务保证「会话头 + 全部消息」要么全写要么不写。
 */
export function saveSession(root, payload) {
  const db = open(root)
  if (!db) return { ok: false, error: 'sqlite unavailable' }
  try {
    const id = String(payload.id || '').trim()
    if (!id) throw new Error('session id required')
    const messages = Array.isArray(payload.messages) ? payload.messages : []
    const t = now()
    db.exec('BEGIN')
    db.prepare(
      'INSERT INTO sessions (id, title, repo, model, cot, tree_depth, created_at, updated_at) '
      + 'VALUES (?, ?, ?, ?, ?, ?, ?, ?) '
      + 'ON CONFLICT(id) DO UPDATE SET title=excluded.title, repo=excluded.repo, '
      + 'model=excluded.model, cot=excluded.cot, tree_depth=excluded.tree_depth, updated_at=excluded.updated_at'
    ).run(
      id, String(payload.title || '新会话'), String(payload.repo || 'codeb'),
      String(payload.model || ''), payload.cot ? 1 : 0, Number(payload.tree_depth) || 3,
      Number(payload.created_at) || t, t,
    )
    const del = db.prepare('DELETE FROM messages WHERE session_id = ?')
    del.run(id)
    const ins = db.prepare(
      'INSERT INTO messages (session_id, seq, role, text, cot, tools_json, llm_json, '
      + 'usage_json, error, stopped, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    )
    for (let i = 0; i < messages.length; i++) {
      const m = messages[i] || {}
      ins.run(
        id, i, String(m.role || 'user'), String(m.text || ''), String(m.cot || ''),
        JSON.stringify(m.tools || []), JSON.stringify(m.llm || []),
        JSON.stringify(m.usage || {}),
        String(m.error || ''), m.stopped ? 1 : 0, t,
      )
    }
    db.exec('COMMIT')
    return { ok: true, id, count: messages.length }
  } catch (e) {
    try { db.exec('ROLLBACK') } catch { /* ignore */ }
    return { ok: false, error: String(e?.message || e) }
  } finally {
    try { db.close() } catch { /* ignore */ }
  }
}

/** 删除一个会话及其消息。 */
export function deleteSession(root, id) {
  const db = open(root)
  if (!db) return { ok: false, error: 'sqlite unavailable' }
  try {
    db.exec('BEGIN')
    db.prepare('DELETE FROM messages WHERE session_id = ?').run(id)
    db.prepare('DELETE FROM sessions WHERE id = ?').run(id)
    db.exec('COMMIT')
    return { ok: true }
  } catch (e) {
    try { db.exec('ROLLBACK') } catch { /* ignore */ }
    return { ok: false, error: String(e?.message || e) }
  } finally {
    try { db.close() } catch { /* ignore */ }
  }
}

function safeParse(s, fallback) {
  try { return JSON.parse(s) } catch { return fallback }
}
