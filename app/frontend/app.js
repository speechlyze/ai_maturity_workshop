/* ======================================================================
   The AI Maturity Ladder — single-page app
   Vanilla JS. Hash router, theme toggle, SSE-over-fetch streaming client,
   and one interactive view per form factor.
   ====================================================================== */

// ── icons ──────────────────────────────────────────────────────────────
const I = {
  ladder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M7 3v18M17 3v18M7 7h10M7 12h10M7 17h10"/></svg>',
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>',
  chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.5 7.2L4 20l1-4.5A8 8 0 1 1 21 12Z"/></svg>',
  rag: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5.5" rx="7" ry="2.7"/><path d="M5 5.5v6c0 1.5 3.1 2.7 7 2.7s7-1.2 7-2.7v-6"/><path d="M5 11.5v6c0 1.5 3.1 2.7 7 2.7s7-1.2 7-2.7v-6"/></svg>',
  flow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="6" rx="1.5"/><rect x="14" y="9" width="7" height="6" rx="1.5"/><rect x="3" y="15" width="7" height="6" rx="1.5"/><path d="M10 6h2.5a1.5 1.5 0 0 1 1.5 1.5V9M10 18h2.5a1.5 1.5 0 0 0 1.5-1.5V15"/></svg>',
  agent: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="7" width="14" height="12" rx="2.5"/><path d="M12 7V4M9 3.5h6M9 12h.01M15 12h.01M9.5 16h5"/></svg>',
  build: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m8 8-4 4 4 4M16 8l4 4-4 4"/><path d="m13.5 5-3 14"/></svg>',
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M19.4 4.6l-1.8 1.8M6.4 17.6l-1.8 1.8"/></svg>',
  moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13.5A8 8 0 1 1 10.5 4 6.3 6.3 0 0 0 20 13.5Z"/></svg>',
  send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m4 12 16-8-6 16-3-7-7-1Z"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
  play: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M7 5.5v13l11-6.5z" fill="currentColor"/></svg>',
  refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8M21 4v4h-4M21 12a9 9 0 0 1-15.5 6.2L3 16M3 20v-4h4"/></svg>',
  tool: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 6.5a3.5 3.5 0 0 0 4.6 4.6l-9 9a2.1 2.1 0 0 1-3-3l9-9a3.5 3.5 0 0 1-1.6-1.6Z"/></svg>',
  bot: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M5 9h14a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2ZM9 13h.01M15 13h.01"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5 9 17.5 20 6.5"/></svg>',
  alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v4M12 17h.01M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>',
  file: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>',
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
};

// ── form factors ─────────────────────────────────────────────────────
const FF = [
  {
    id: "chatbot", rung: 1, nav: "LLM Chatbot", icon: I.chat, accent: "var(--r1)",
    title: "The Chatbot", kicker: "Form Factor 01 — Generate text",
    desc: "The simplest useful thing you can build with Claude: send a question, get an answer. No database, no tools, no retrieval. Memory is just the growing list of messages you resend each turn.",
    term: "<b>LLM (Large Language Model):</b> a model trained to predict text. On its own it has no memory between calls, no access to your data, and no ability to act. It maps a prompt to a response — nothing more.",
    meta: { Flow: "You — one call", Data: "Training data only", Acts: "No" },
  },
  {
    id: "rag", rung: 2, nav: "RAG Chatbot", icon: I.rag, accent: "var(--r2)",
    title: "Retrieval-Augmented Generation", kicker: "Form Factor 02 — Ground in your data",
    desc: "The same LLM, now grounded in Acme Cloud's real documentation stored in Oracle AI Database. Retrieve the relevant docs first, then hand them to the model with the question — answers reflect real data, with citations.",
    term: "<b>RAG:</b> retrieve the documents relevant to a question, then hand them to the LLM alongside the question. Retrieval quality is the single biggest lever on answer quality — compare vector, keyword, and hybrid below.",
    meta: { Flow: "You — retrieve → generate", Data: "+ Your documents", Acts: "No" },
  },
  {
    id: "workflow", rung: 3, nav: "LLM Workflow", icon: I.flow, accent: "var(--r3)",
    title: "The LLM-Driven Workflow", kicker: "Form Factor 03 — Reliable pipelines",
    desc: "Several LLM calls and ordinary code composed into a fixed, predictable pipeline: classify → route → retrieve → draft → review-and-revise. Your code owns the sequence; the model fills in each step.",
    term: "<b>Workflow:</b> the steps are decided by you, in code. Breaking a task into small, single-purpose steps with checks between them yields far more consistent results than one big do-everything prompt.",
    meta: { Flow: "Your code — fixed steps", Data: "+ Your documents", Acts: "Within the pipeline" },
  },
  {
    id: "agent", rung: 4, nav: "Autonomous Agent", icon: I.agent, accent: "var(--r4)",
    title: "The Agent", kicker: "Form Factor 04 — Model-chosen tools",
    desc: "An LLM running in a loop with tools. The model decides which tool to call, inspects the result, and decides what to do next — repeating until the job is done. We give it two tools (search the docs, open a ticket) and a goal.",
    term: "<b>Agent:</b> an LLM in a loop with tools. Unlike a workflow, the model chooses the trajectory. Built on the <code>claude-agent-sdk</code> — the same runtime that powers Claude Code.",
    meta: { Flow: "The model — dynamic", Data: "+ Tools you provide", Acts: "Via tools" },
  },
  {
    id: "builder", rung: 5, nav: "Agent That Builds", icon: I.build, accent: "var(--r5)",
    title: "The Autonomous Agent", kicker: "Form Factor 05 — Write & run code",
    desc: "The top rung: an agent equipped with file and shell tools that doesn't just answer — it writes a script, runs it, and fixes its own errors until it works. It produces durable automation, all on its own.",
    term: "<b>Autonomous agent:</b> an agent with tools that change the world — here, writing files and running shell commands inside a sandbox. From answering to building.",
    meta: { Flow: "The model — dynamic", Data: "+ Files & shell", Acts: "Yes — writes & runs code" },
  },
];
const FF_BY_ID = Object.fromEntries(FF.map((f) => [f.id, f]));

// ── tiny utils ─────────────────────────────────────────────────────────
const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36);

function renderRich(text) {
  let h = esc(text);
  h = h.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  h = h.replace(/`([^`]+?)`/g, "<code>$1</code>");
  h = h.replace(/\[(\d+)\]/g, '<span class="cite">[$1]</span>');
  return h.split(/\n{2,}/).map((p) => "<p>" + p.replace(/\n/g, "<br>") + "</p>").join("");
}

// SSE-over-fetch: POST a JSON body, parse the text/event-stream response.
async function streamSSE(url, body, onEvent, signal) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) throw new Error("HTTP " + res.status);
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const SEP = /\r?\n\r?\n/;
    let m;
    while ((m = SEP.exec(buf))) {
      const block = buf.slice(0, m.index);
      buf = buf.slice(m.index + m[0].length);
      let event = "message", data = "";
      for (const line of block.split(/\r?\n/)) {
        if (line.startsWith(":")) continue;
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).replace(/^\s/, "");
      }
      if (event === "end") return;
      if (data) { try { onEvent(JSON.parse(data)); } catch (_) {} }
    }
  }
}

async function getJSON(url) { const r = await fetch(url); return r.json(); }

// ── app state ──────────────────────────────────────────────────────────
const state = {
  health: null,
  chatSession: uid(),
  abort: null, // current streaming AbortController
};

function cancelStream() {
  if (state.abort) { try { state.abort.abort(); } catch (_) {} state.abort = null; }
}

// ── sidebar ──────────────────────────────────────────────────────────
function renderSidebar(activeId) {
  const items = [
    `<a class="nav-item nav-home ${activeId === "home" ? "active" : ""}" href="#/" style="--c:var(--text-2);animation-delay:0ms">
       <span class="nav-node">${I.home}</span><span class="nav-label">Overview</span>
     </a>`,
    ...FF.map((f, i) => `
      <a class="nav-item ${activeId === f.id ? "active" : ""}" href="#/${f.id}" style="--c:${f.accent};animation-delay:${(i + 1) * 55}ms">
        <span class="nav-node">${f.rung}</span>
        <span class="nav-label">${f.nav}</span>
        <span class="nav-rung">${f.icon}</span>
      </a>`),
  ].join("");

  $("#sidebar").innerHTML = `
    <div class="brand">
      <span class="brand-glyph">${I.ladder}</span>
      <span class="brand-text"><b>Maturity Ladder</b><span>Five AI form factors</span></span>
    </div>
    <div class="rail-label">The Ladder</div>
    <nav class="ladder-rail">${items}</nav>
    <div class="sidebar-foot">
      <div class="status-card" id="status-card">${statusInner()}</div>
      <button class="theme-toggle" id="theme-toggle">
        <span style="display:flex;align-items:center;gap:8px">${themeIcon()} <span id="theme-label">${themeLabel()}</span></span>
        <span class="toggle-track"></span>
      </button>
    </div>`;

  $("#theme-toggle").addEventListener("click", toggleTheme);
}

function statusInner() {
  const h = state.health;
  if (!h) return `<div class="status-row"><span class="dot pulse"></span><span class="muted">Connecting…</span></div>`;
  const rb = h.retrieval || {};
  const ready = rb.ready;
  const backend = rb.backend === "oracle" ? "Oracle AI DB" : rb.backend === "memory" ? "In-memory" : "warming…";
  const rdot = !ready ? "warn pulse" : "ok";
  const adot = h.agent_available ? "ok" : "off";
  return `
    <div class="status-row"><span class="k">Model</span><span class="mono" style="color:var(--text)">${esc(h.model)}</span></div>
    <div class="status-row"><span class="k">Retrieval</span><span class="dot ${rdot}"></span><span>${backend}</span></div>
    <div class="status-row"><span class="k">Agents</span><span class="dot ${adot}"></span><span>${h.agent_available ? "ready" : "CLI not found"}</span></div>`;
}

function themeIcon() { return document.documentElement.getAttribute("data-theme") === "light" ? I.sun : I.moon; }
function themeLabel() { return document.documentElement.getAttribute("data-theme") === "light" ? "Light" : "Dark"; }
function toggleTheme() {
  const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  try { localStorage.setItem("aiml-theme", next); } catch (_) {}
  $("#theme-label").textContent = themeLabel();
  $("#theme-toggle").querySelector("svg").outerHTML = themeIcon();
}

function refreshStatus() { const c = $("#status-card"); if (c) c.innerHTML = statusInner(); }

// ── header / shells ──────────────────────────────────────────────────
function ffHeader(f) {
  return `
    <header class="ff-head">
      <div class="ff-numeral">${f.rung}</div>
      <div class="ff-head-body">
        <div class="ff-kicker">${esc(f.kicker)}</div>
        <h1 class="ff-title">${esc(f.title)}</h1>
        <p class="ff-desc">${esc(f.desc)}</p>
        <div class="ff-term">${f.term}</div>
      </div>
    </header>`;
}

function setStage(html, accent) {
  const stage = $("#stage");
  stage.style.setProperty("--accent", accent || "var(--r5)");
  stage.innerHTML = `<div class="view view-enter">${html}</div>`;
  stage.scrollTop = 0;
}

// ── view: home ─────────────────────────────────────────────────────────
function viewHome() {
  const rungs = FF.map((f, i) => `
    <a class="rung" href="#/${f.id}" style="--c:${f.accent};animation-delay:${i * 70 + 80}ms">
      <div class="rung-num">${f.rung}</div>
      <div class="rung-main">
        <h3>${esc(f.nav)} <span class="muted" style="font-weight:400;font-size:14px">· ${esc(f.title)}</span></h3>
        <p>${esc(f.desc)}</p>
      </div>
      <div class="rung-meta">
        ${Object.entries(f.meta).map(([k, v]) => `<div class="meta-line"><span class="mk">${k}</span><span class="mv">${esc(v)}</span></div>`).join("")}
      </div>
      <div class="rung-go">${I.arrow}</div>
    </a>`).join("");

  setStage(`
    <section class="hero">
      <div class="hero-kicker"><span class="pip"></span> The AI Maturity Ladder</div>
      <h1>Climb from a plain chatbot to an agent that <em>writes &amp; runs its own code</em> — one rung at a time.</h1>
      <p>One running example — a support assistant for the fictional <b>Acme Cloud</b> — built five ways, each adding exactly one new capability. Naming that difference tells you the simplest form factor that solves your problem.</p>
    </section>
    <div class="ladder">${rungs}</div>`, "var(--r5)");
}

// ── view: chatbot (FF1) ─────────────────────────────────────────────────
function viewChatbot() {
  const f = FF_BY_ID.chatbot;
  setStage(`${ffHeader(f)}
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title">${I.chat} Conversation</span>
        <button class="btn btn-ghost" id="new-chat">${I.refresh} New chat</button>
      </div>
      <div class="panel-body">
        <div class="chat-wrap">
          <div class="chat-scroll" id="chat-scroll">
            <div class="empty">Ask anything. Each reply re-sends the whole conversation — that's the "memory".</div>
          </div>
          <div class="memory-note" id="mem-note"></div>
          <div class="composer">
            <textarea id="chat-input" placeholder="Message Claude…  (e.g. My name is Sam and I'm an analytics engineer)" rows="1"></textarea>
            <button class="btn btn-accent" id="chat-send">${I.send} Send</button>
          </div>
        </div>
      </div>
    </div>`, f.accent);

  const scroll = $("#chat-scroll"), input = $("#chat-input"), send = $("#chat-send");
  let first = true;

  async function sendMsg() {
    const text = input.value.trim();
    if (!text || state.abort) return;
    if (first) { scroll.innerHTML = ""; first = false; }
    input.value = ""; autosize(input);
    addMsg(scroll, "user", text);
    const bubble = addMsg(scroll, "bot", "");
    bubble.innerHTML = '<span class="caret"></span>';
    send.disabled = true;
    let acc = "";
    state.abort = new AbortController();
    try {
      await streamSSE("/api/chat/message", { session_id: state.chatSession, message: text }, (ev) => {
        if (ev.type === "delta") { acc += ev.text; bubble.innerHTML = renderRich(acc) + '<span class="caret"></span>'; scroll.scrollTop = scroll.scrollHeight; }
        else if (ev.type === "done") { bubble.innerHTML = renderRich(acc); $("#mem-note").innerHTML = `memory: <b>${ev.turns}</b> messages re-sent on the next turn`; }
      }, state.abort.signal);
    } catch (e) { bubble.innerHTML = `<span style="color:var(--r5)">Error: ${esc(e.message)}</span>`; }
    finally { state.abort = null; send.disabled = false; input.focus(); }
  }

  send.addEventListener("click", sendMsg);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMsg(); } });
  input.addEventListener("input", () => autosize(input));
  $("#new-chat").addEventListener("click", async () => {
    cancelStream();
    await fetch("/api/chat/reset?session_id=" + state.chatSession, { method: "POST" }).catch(() => {});
    state.chatSession = uid();
    scroll.innerHTML = `<div class="empty">New conversation. Previous memory cleared.</div>`;
    $("#mem-note").innerHTML = ""; first = true;
  });
  input.focus();
}

function addMsg(scroll, role, text) {
  const wrap = document.createElement("div");
  wrap.className = "msg " + role;
  wrap.innerHTML = `<div class="avatar ${role}">${role === "bot" ? I.bot : "YOU"}</div><div class="bubble">${role === "bot" ? "" : renderRich(text)}</div>`;
  scroll.appendChild(wrap);
  scroll.scrollTop = scroll.scrollHeight;
  return wrap.querySelector(".bubble");
}
function autosize(el) { el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 160) + "px"; }

// ── view: RAG (FF2) ─────────────────────────────────────────────────────
const RAG_SAMPLES = [
  "What is the exact API rate limit on the Pro plan?",
  "How do I keep my data safe and recoverable?",
  "Which plans include SSO?",
  "How long are backups retained?",
];
function viewRAG() {
  const f = FF_BY_ID.rag;
  setStage(`${ffHeader(f)}
    <div class="panel mb">
      <div class="panel-body">
        <div class="row spread mb">
          <div class="row">
            <span class="hint mono">Technique</span>
            <div class="seg" id="rag-tech">
              <button class="active" data-t="vector">Vector</button>
              <button data-t="keyword">Keyword</button>
              <button data-t="hybrid">Hybrid · RRF</button>
            </div>
          </div>
          <span class="hint" id="rag-backend"></span>
        </div>
        <div class="field">
          <textarea id="rag-input" rows="1" placeholder="Ask about Acme Cloud…"></textarea>
          <button class="btn btn-accent" id="rag-ask">${I.send} Ask</button>
        </div>
        <div class="chips mb" style="margin-top:12px">${RAG_SAMPLES.map((s) => `<button class="chip">${esc(s)}</button>`).join("")}</div>
      </div>
    </div>
    <div class="grid-2">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">${I.bot} Grounded answer</span></div>
        <div class="panel-body"><div id="rag-answer" class="bubble" style="background:transparent;border:none;padding:0"><div class="empty">The answer will cite its sources like [1].</div></div></div>
      </div>
      <div class="panel">
        <div class="panel-head"><span class="panel-title">${I.rag} Retrieved context</span></div>
        <div class="panel-body"><div id="rag-sources" class="sources"><div class="empty">Retrieved documents appear here.</div></div></div>
      </div>
    </div>`, f.accent);

  let technique = "vector";
  const seg = $("#rag-tech"), input = $("#rag-input"), ask = $("#rag-ask");
  seg.addEventListener("click", (e) => {
    const b = e.target.closest("button"); if (!b) return;
    seg.querySelectorAll("button").forEach((x) => x.classList.toggle("active", x === b));
    technique = b.dataset.t;
  });
  $$(".chip", $("#stage")).forEach((c) => c.addEventListener("click", () => { input.value = c.textContent; runRAG(); }));

  async function runRAG() {
    const q = input.value.trim();
    if (!q || state.abort) return;
    const ans = $("#rag-answer"), src = $("#rag-sources");
    ans.innerHTML = '<span class="caret"></span>'; src.innerHTML = `<div class="empty"><span class="spinner" style="display:inline-block"></span> retrieving…</div>`;
    ask.disabled = true;
    let acc = "";
    state.abort = new AbortController();
    try {
      await streamSSE("/api/rag/answer", { query: q, technique, k: 4 }, (ev) => {
        if (ev.type === "sources") {
          $("#rag-backend").innerHTML = `backend: <b class="mono" style="color:var(--accent)">${ev.backend === "oracle" ? "Oracle AI Database" : "in-memory NumPy"}</b> · ${ev.technique}`;
          src.innerHTML = ev.hits.length ? ev.hits.map((h, i) => sourceCard(h, i)).join("") : `<div class="empty">No matches for this technique.</div>`;
        } else if (ev.type === "delta") { acc += ev.text; ans.innerHTML = renderRich(acc) + '<span class="caret"></span>'; }
        else if (ev.type === "done") { ans.innerHTML = renderRich(acc) || `<div class="empty">No answer.</div>`; }
      }, state.abort.signal);
    } catch (e) { ans.innerHTML = `<span style="color:var(--r5)">Error: ${esc(e.message)}</span>`; }
    finally { state.abort = null; ask.disabled = false; }
  }
  ask.addEventListener("click", runRAG);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); runRAG(); } });
  input.addEventListener("input", () => autosize(input));
  input.focus();
}
function sourceCard(h, i) {
  return `<div class="source" style="animation-delay:${i * 50}ms">
    <div class="source-top"><span class="source-idx">${i + 1}</span><span class="source-title">${esc(h.title)}</span><span class="source-cat">${esc(h.category)}</span><span class="source-score">${(+h.score).toFixed(3)}</span></div>
    <div class="source-body">${esc(h.content)}</div></div>`;
}

// ── view: workflow (FF3) ────────────────────────────────────────────────
const WF_SAMPLES = [
  "I've been double-charged for my Pro seats this month and need this fixed before our board demo tomorrow.",
  "How do I rotate my API keys without breaking my app?",
  "Can I change my project's region after creation?",
];
const WF_STAGES = { classify: "Classify", route: "Route", retrieve: "Retrieve", draft: "Draft reply", review: "Review" };
function viewWorkflow() {
  const f = FF_BY_ID.workflow;
  setStage(`${ffHeader(f)}
    <div class="panel mb">
      <div class="panel-body">
        <div class="field">
          <textarea id="wf-input" rows="2" placeholder="Paste an incoming support message…">${esc(WF_SAMPLES[0])}</textarea>
          <button class="btn btn-accent" id="wf-run">${I.play} Run pipeline</button>
        </div>
        <div class="chips" style="margin-top:12px">${WF_SAMPLES.map((s) => `<button class="chip">${esc(s.slice(0, 46))}…</button>`).join("")}</div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-head"><span class="panel-title">${I.flow} Fixed pipeline · your code owns the flow</span><span class="hint mono" id="wf-status"></span></div>
      <div class="panel-body"><div class="pipeline" id="wf-pipe"><div class="empty">Run the pipeline to watch each stage execute in order.</div></div></div>
    </div>`, f.accent);

  const input = $("#wf-input"), run = $("#wf-run"), pipe = $("#wf-pipe");
  $$(".chip", $("#stage")).forEach((c, i) => c.addEventListener("click", () => { input.value = WF_SAMPLES[i]; autosize(input); }));

  async function runWF() {
    const message = input.value.trim();
    if (!message || state.abort) return;
    pipe.innerHTML = ""; run.disabled = true; $("#wf-status").textContent = "running…";
    const pending = {};
    state.abort = new AbortController();
    try {
      await streamSSE("/api/workflow/run", { message, max_revisions: 1 }, (ev) => {
        if (ev.type === "step") {
          if (ev.status === "running") { pending[ev.step] = addStage(pipe, ev.step); }
          else if (ev.status === "done") { fillStage(pending[ev.step] || addStage(pipe, ev.step), ev.step, ev.data); pending[ev.step] = null; }
        } else if (ev.type === "final") {
          $("#wf-status").textContent = "done";
          const box = document.createElement("div");
          box.className = "stage-row done"; box.style.animationDelay = "0ms";
          box.innerHTML = `<div class="stage-rail"><div class="stage-dot">${I.check}</div></div>
            <div class="stage-card" style="border-color:color-mix(in oklab,var(--accent) 30%,transparent)">
              <div class="stage-name">Final reply ${ev.escalated ? '<span class="tag high">escalated</span>' : '<span class="tag ok">auto-handled</span>'}</div>
              <div class="final-reply">${renderRich(ev.reply)}</div></div>`;
          pipe.appendChild(box);
        }
      }, state.abort.signal);
    } catch (e) { pipe.insertAdjacentHTML("beforeend", `<div class="banner warn">${I.alert}<div>Error: ${esc(e.message)}</div></div>`); }
    finally { state.abort = null; run.disabled = false; }
  }
  run.addEventListener("click", runWF);
  autosize(input);
}
function addStage(pipe, step) {
  if (pipe.querySelector(".empty")) pipe.innerHTML = "";
  const row = document.createElement("div");
  row.className = "stage-row running";
  row.innerHTML = `<div class="stage-rail"><div class="stage-dot"><span class="spinner"></span></div><div class="stage-line"></div></div>
    <div class="stage-card"><div class="stage-name">${esc(WF_STAGES[step] || step)} <span class="stage-sub">working…</span></div><div class="stage-content"></div></div>`;
  pipe.appendChild(row);
  pipe.scrollIntoView; return row;
}
function fillStage(row, step, data) {
  if (!row) return;
  row.className = "stage-row done";
  const dot = $(".stage-dot", row); const n = Object.keys(WF_STAGES).indexOf(step) + 1;
  dot.innerHTML = step === "review" ? (data.approved ? I.check : "↻") : String(n || "•");
  const name = $(".stage-name", row), content = $(".stage-content", row);
  if (step === "classify") {
    name.innerHTML = `Classify <span class="stage-sub">structured output</span>`;
    content.innerHTML = `<span class="kv">category <b>${esc(data.category)}</b></span><span class="kv">urgency <span class="tag ${esc(data.urgency)}">${esc(data.urgency)}</span></span><div style="margin-top:6px">${esc(data.summary)}</div>`;
  } else if (step === "route") {
    name.innerHTML = `Route <span class="stage-sub">your code decides</span>`;
    content.innerHTML = `${data.escalated ? '<span class="tag high">escalate → human</span>' : '<span class="tag ok">automated</span>'} <span class="muted">${esc(data.reason)}</span>`;
  } else if (step === "retrieve") {
    name.innerHTML = `Retrieve <span class="stage-sub">${data.hits.length} docs · ${esc(data.backend)}</span>`;
    content.innerHTML = `<div class="chips">${data.hits.map((h) => `<span class="chip" style="cursor:default">${esc(h.title)}</span>`).join("")}</div>`;
  } else if (step === "draft") {
    name.innerHTML = `Draft reply <span class="stage-sub">attempt ${data.attempt}${data.revising ? " · revising" : ""}</span>`;
    content.innerHTML = data.draft ? renderRich(data.draft) : "";
  } else if (step === "review") {
    name.innerHTML = `Review <span class="stage-sub">attempt ${data.attempt} · QA gate</span>`;
    content.innerHTML = `${data.approved ? '<span class="tag ok">approved</span>' : '<span class="tag no">needs revision</span>'} <span class="muted">${esc(data.feedback || "")}</span>`;
  }
}

// ── agent log (shared by FF4 & FF5) ────────────────────────────────────
function addEvent(log, ev) {
  if (log.querySelector(".empty")) log.innerHTML = "";
  const node = document.createElement("div");
  if (ev.type === "text") {
    if (!ev.text || !ev.text.trim()) return null;
    node.className = "ev text"; node.innerHTML = `<div class="ev-icon">${I.bot}</div><div class="ev-text"><div class="ev-bubble">${renderRich(ev.text)}</div></div>`;
  } else if (ev.type === "tool_use") {
    const args = Object.entries(ev.input || {}).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(", ");
    node.className = "ev tool"; node.innerHTML = `<div class="ev-icon">${I.tool}</div><div class="ev-text"><div class="ev-bubble"><span class="tname">${esc(ev.name)}</span>(<span class="tool-args">${esc(args)}</span>)</div></div>`;
  } else if (ev.type === "tool_result") {
    node.className = "ev result"; node.innerHTML = `<div class="ev-icon">${I.check}</div><div class="ev-text"><div class="ev-bubble mono" style="font-size:12.5px;white-space:pre-wrap">${esc(ev.text)}</div></div>`;
  } else if (ev.type === "result") {
    node.className = "ev result"; const bits = [];
    if (ev.num_turns != null) bits.push(`${ev.num_turns} turns`);
    if (ev.duration_ms != null) bits.push(`${(ev.duration_ms / 1000).toFixed(1)}s`);
    if (ev.cost_usd != null) bits.push(`$${(+ev.cost_usd).toFixed(4)}`);
    node.className = "ev result"; node.innerHTML = `<div class="ev-icon">${I.check}</div><div class="ev-text"><div class="ev-meta">agent finished · ${bits.join(" · ") || "ok"}</div></div>`;
  } else if (ev.type === "error") {
    node.className = "ev err"; node.innerHTML = `<div class="ev-icon">${I.alert}</div><div class="ev-text"><div class="ev-bubble">${esc(ev.message)}</div></div>`;
  } else return null;
  log.appendChild(node); log.scrollTop = log.scrollHeight; return node;
}

// ── view: agent (FF4) ───────────────────────────────────────────────────
const AGENT_SAMPLES = [
  "I'm on the Pro plan and keep hitting rate limits right before our launch tomorrow. What are my options, and can you escalate this for me?",
  "What's included in the Enterprise plan?",
  "My webhooks stopped firing and it's urgent — please look into it and open a ticket.",
];
function viewAgent() {
  const f = FF_BY_ID.agent;
  const unavailable = state.health && !state.health.agent_available;
  setStage(`${ffHeader(f)}
    ${unavailable ? agentBanner() : ""}
    <div class="panel mb">
      <div class="panel-body">
        <div class="field">
          <textarea id="ag-input" rows="2" placeholder="Give the agent a goal…">${esc(AGENT_SAMPLES[0])}</textarea>
          <button class="btn btn-accent" id="ag-run" ${unavailable ? "disabled" : ""}>${I.play} Run agent</button>
        </div>
        <div class="chips" style="margin-top:12px">${AGENT_SAMPLES.map((s, i) => `<button class="chip">${esc(i === 0 ? "Rate limits + escalate" : s.slice(0, 40) + "…")}</button>`).join("")}</div>
        <div class="hint" style="margin-top:10px">Tools: <span class="mono" style="color:var(--accent)">search_docs</span>, <span class="mono" style="color:var(--accent)">create_support_ticket</span> — the model chooses which to call, and when.</div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-head"><span class="panel-title">${I.agent} Agent trajectory</span><span class="hint mono" id="ag-status"></span></div>
      <div class="panel-body"><div class="log" id="ag-log"><div class="empty">The agent's reasoning and tool calls stream here as it decides its own path.</div></div></div>
    </div>`, f.accent);

  const input = $("#ag-input"), run = $("#ag-run"), log = $("#ag-log");
  $$(".chip", $("#stage")).forEach((c, i) => c.addEventListener("click", () => { input.value = AGENT_SAMPLES[i]; autosize(input); }));
  run && run.addEventListener("click", async () => {
    const prompt = input.value.trim(); if (!prompt || state.abort) return;
    log.innerHTML = ""; run.disabled = true; $("#ag-status").innerHTML = '<span class="spinner" style="display:inline-block"></span>';
    state.abort = new AbortController();
    try { await streamSSE("/api/agent/run", { prompt }, (ev) => addEvent(log, ev), state.abort.signal); }
    catch (e) { addEvent(log, { type: "error", message: e.message }); }
    finally { state.abort = null; run.disabled = false; $("#ag-status").textContent = "done"; }
  });
  autosize(input);
}
function agentBanner() {
  return `<div class="banner warn">${I.alert}<div>The Claude Agent SDK CLI wasn't found, so Form Factors 4 &amp; 5 are disabled. Install it with <span class="mono">npm i -g @anthropic-ai/claude-code</span> and restart the server.</div></div>`;
}

// ── view: builder (FF5) ─────────────────────────────────────────────────
function viewBuilder() {
  const f = FF_BY_ID.builder;
  const unavailable = state.health && !state.health.agent_available;
  setStage(`${ffHeader(f)}
    ${unavailable ? agentBanner() : `<div class="banner warn">${I.alert}<div>This agent executes code (Write / Edit / Bash) with permissions bypassed, confined to a sandbox directory. That's the point of the demo — run it locally.</div></div>`}
    <div class="panel mb">
      <div class="panel-body">
        <div class="row spread mb"><span class="panel-title">${I.build} Build task</span><span class="hint mono">sandbox seeded with <b>support_messages.csv</b></span></div>
        <textarea id="bd-input" rows="6" placeholder="Describe what to build…"></textarea>
        <div class="row" style="margin-top:12px">
          <button class="btn btn-accent" id="bd-run" ${unavailable ? "disabled" : ""}>${I.play} Build &amp; run</button>
          <button class="btn btn-ghost" id="bd-reset">${I.refresh} Reset task</button>
        </div>
      </div>
    </div>
    <div class="grid-2">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">${I.agent} Build trajectory</span><span class="hint mono" id="bd-status"></span></div>
        <div class="panel-body"><div class="log" id="bd-log"><div class="empty">The agent writes a script, runs it, and fixes errors until it works.</div></div></div>
      </div>
      <div class="panel">
        <div class="panel-head"><span class="panel-title">${I.file} Sandbox artifacts</span><button class="btn btn-ghost" id="bd-refresh">${I.refresh}</button></div>
        <div class="panel-body"><div class="files" id="bd-files"><div class="empty">Files the agent creates will appear here.</div></div></div>
      </div>
    </div>`, f.accent);

  const input = $("#bd-input"), run = $("#bd-run"), log = $("#bd-log");
  let defaultTask = "";
  getJSON("/api/builder/default-task").then((d) => { defaultTask = d.task || ""; if (!input.value) input.value = defaultTask; autosize2(input); }).catch(() => {});
  loadArtifacts();

  run && run.addEventListener("click", async () => {
    const task = input.value.trim(); if (!task || state.abort) return;
    log.innerHTML = ""; run.disabled = true; $("#bd-status").innerHTML = '<span class="spinner" style="display:inline-block"></span> building…';
    state.abort = new AbortController();
    try {
      await streamSSE("/api/builder/run", { task }, (ev) => {
        if (ev.type === "artifacts_ready") loadArtifacts();
        else addEvent(log, ev);
      }, state.abort.signal);
    } catch (e) { addEvent(log, { type: "error", message: e.message }); }
    finally { state.abort = null; run.disabled = false; $("#bd-status").textContent = "done"; loadArtifacts(); }
  });
  $("#bd-reset").addEventListener("click", () => { input.value = defaultTask; autosize2(input); });
  $("#bd-refresh").addEventListener("click", loadArtifacts);
}
async function loadArtifacts() {
  const box = $("#bd-files"); if (!box) return;
  try {
    const d = await getJSON("/api/builder/artifacts");
    if (!d.files || !d.files.length) { box.innerHTML = `<div class="empty">No files yet.</div>`; return; }
    box.innerHTML = d.files.map((file, i) => {
      const isNew = file.name !== "support_messages.csv";
      const body = file.content != null
        ? `<div class="filebox"><pre>${esc(file.content)}</pre></div>`
        : (file.truncated ? `<div class="filebox"><pre class="muted">(file too large to preview)</pre></div>` : "");
      return `<div class="file">
        <div class="file-head" data-i="${i}">${I.file}<span class="file-name">${esc(file.name)}</span>${isNew ? '<span class="file-new">new</span>' : ""}<span class="file-size">${file.size} B</span></div>
        ${body}</div>`;
    }).join("");
    $$(".file-head", box).forEach((h) => h.addEventListener("click", () => { const b = h.nextElementSibling; if (b && b.classList.contains("filebox")) b.style.display = b.style.display === "none" ? "" : "none"; }));
  } catch (_) { box.innerHTML = `<div class="empty">Couldn't load artifacts.</div>`; }
}
function autosize2(el) { if (el) { el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 260) + "px"; } }

// helper: querySelectorAll
function $$(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

// ── router ───────────────────────────────────────────────────────────
const ROUTES = { "": viewHome, chatbot: viewChatbot, rag: viewRAG, workflow: viewWorkflow, agent: viewAgent, builder: viewBuilder };
function route() {
  cancelStream();
  const id = (location.hash.replace(/^#\/?/, "").trim()) || "";
  const render = ROUTES[id] || viewHome;
  renderSidebar(id || "home");
  render();
  if (window.innerWidth <= 760) closeMenu();
}

// ── mobile menu ──────────────────────────────────────────────────────
function openMenu() { $("#sidebar").classList.add("open"); const s = $("#scrim"); s.hidden = false; }
function closeMenu() { $("#sidebar").classList.remove("open"); $("#scrim").hidden = true; }

// ── boot ─────────────────────────────────────────────────────────────
async function boot() {
  // mobile menu button
  const mb = document.createElement("button");
  mb.className = "menu-btn"; mb.innerHTML = I.menu; mb.setAttribute("aria-label", "Menu");
  mb.addEventListener("click", openMenu); document.body.appendChild(mb);
  $("#scrim").addEventListener("click", closeMenu);

  window.addEventListener("hashchange", route);
  route();

  // poll health until retrieval is warm
  async function poll() {
    try { state.health = await getJSON("/api/health"); refreshStatus(); }
    catch (_) {}
    if (!state.health || !state.health.retrieval || !state.health.retrieval.ready) setTimeout(poll, 1500);
  }
  poll();
}
boot();
