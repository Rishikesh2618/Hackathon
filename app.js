/**
 * FarmAI – Frontend Application
 * Connects to FastAPI backend for semantic search & multilingual Q&A
 */

const API_BASE = window.location.origin;   // same-origin → FastAPI serves this

let currentCategory = 'all';
let currentLang     = 'en';
let isListening     = false;
let recognition     = null;
let messageCount    = 0;

// ─── Init ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  initVoice();
  document.getElementById('langSelect').addEventListener('change', onLanguageChange);
  loadSuggestions(currentLang);
  setInterval(checkHealth, 30_000);   // health-check every 30 s
});

// ─── Health Check ──────────────────────────────────────────────────
async function checkHealth() {
  const dot  = document.getElementById('statusDot');
  const text = document.getElementById('statusText');
  try {
    const res = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(5000) });
    if (res.ok) {
      dot.className  = 'status-dot';
      text.textContent = 'Connected';
    } else {
      throw new Error('not ok');
    }
  } catch {
    dot.className    = 'status-dot offline';
    text.textContent = 'Offline';
  }
}

// ─── Language ──────────────────────────────────────────────────────
function onLanguageChange(e) {
  currentLang = e.target.value;
  loadSuggestions(currentLang);
  showToast('🌐 Language changed. Your queries will be answered in the selected language.');
}

async function loadSuggestions(lang) {
  try {
    const res  = await fetch(`${API_BASE}/api/suggestions?lang=${lang}`);
    const data = await res.json();
    const box  = document.getElementById('suggestionsList');
    box.innerHTML = data.suggestions
      .map(s => `<button class="suggestion-btn" onclick="askSuggestion(this)">${escHtml(s)}</button>`)
      .join('');
  } catch {
    // keep default suggestions
  }
}

// ─── Category ─────────────────────────────────────────────────────
function setCategory(btn, cat) {
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentCategory = cat;
  const label = document.getElementById('catLabel');
  if (cat === 'all') {
    label.textContent = '';
    label.classList.remove('visible');
  } else {
    label.textContent = `Filter: ${cat}`;
    label.classList.add('visible');
  }
}

// ─── Send Query ────────────────────────────────────────────────────
async function sendQuery() {
  const input = document.getElementById('queryInput');
  const query = input.value.trim();
  if (!query) { showToast('Please type your question first.'); return; }

  input.value = '';
  hideWelcome();

  appendUserMessage(query);
  const typingId = appendTyping();

  const sendBtn = document.getElementById('sendBtn');
  sendBtn.disabled = true;

  try {
    const payload = {
      query,
      language: currentLang,
      category: currentCategory === 'all' ? null : currentCategory,
      top_k: 3,
    };
    const res  = await fetch(`${API_BASE}/api/query`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    removeElement(typingId);
    appendBotMessage(data);
  } catch (err) {
    removeElement(typingId);
    appendErrorMessage(err.message);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && e.ctrlKey) sendQuery();
}

function askSuggestion(btn) {
  document.getElementById('queryInput').value = btn.textContent.replace(/^→ /, '');
  sendQuery();
}

// ─── Messages ──────────────────────────────────────────────────────
function hideWelcome() {
  const w = document.getElementById('welcomeCard');
  if (w) w.remove();
}

function appendUserMessage(text) {
  const id = `msg-${++messageCount}`;
  const el = document.createElement('div');
  el.className = 'msg-user';
  el.id = id;
  el.innerHTML = `
    <div class="bubble">${escHtml(text)}</div>
    <div class="msg-avatar">👤</div>
  `;
  document.getElementById('messagesContainer').appendChild(el);
  scrollToBottom();
  return id;
}

function appendTyping() {
  const id = `typing-${++messageCount}`;
  const el = document.createElement('div');
  el.className = 'typing-indicator';
  el.id = id;
  el.innerHTML = `
    <div class="msg-avatar">🌾</div>
    <div class="typing-bubble">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  document.getElementById('messagesContainer').appendChild(el);
  scrollToBottom();
  return id;
}

function appendBotMessage(data) {
  const id = `msg-${++messageCount}`;
  const el = document.createElement('div');
  el.className = 'msg-bot';
  el.id = id;

  // Format answer: convert markdown bold (**text**) and newlines
  const formattedAnswer = formatAnswer(data.answer);

  // Sources chips
  let sourcesHtml = '';
  if (data.sources && data.sources.length > 0) {
    const chips = data.sources
      .map(s => `<button class="source-chip" onclick="askSource('${escHtml(s.title)}')" title="Ask about: ${escHtml(s.title)}">${escHtml(s.title)}</button>`)
      .join('');
    sourcesHtml = `<div class="sources-row">${chips}</div>`;
  }

  // Confidence bar
  const confPct = Math.round((data.confidence || 0) * 100);
  const confLabel = confPct > 70 ? 'High confidence' : confPct > 40 ? 'Moderate confidence' : 'Low confidence';

  // Lang badge
  const langBadge = data.detected_lang && data.detected_lang !== 'en'
    ? `<span style="font-size:0.72rem;color:var(--text-light);margin-left:0.5rem">Detected: ${data.detected_lang}</span>`
    : '';

  el.innerHTML = `
    <div class="msg-avatar">🌾</div>
    <div class="bubble-wrap">
      <div class="bubble">${formattedAnswer}</div>
      ${sourcesHtml}
      <div class="confidence-bar">
        <span>${confLabel} (${confPct}%)</span>
        <div class="conf-track"><div class="conf-fill" style="width:0%" data-width="${confPct}%"></div></div>
        ${langBadge}
      </div>
    </div>
  `;
  document.getElementById('messagesContainer').appendChild(el);

  // Animate confidence bar
  setTimeout(() => {
    const fill = el.querySelector('.conf-fill');
    if (fill) fill.style.width = fill.dataset.width;
  }, 100);

  scrollToBottom();
  return id;
}

function appendErrorMessage(errText) {
  const id = `msg-${++messageCount}`;
  const el = document.createElement('div');
  el.className = 'msg-bot';
  el.id = id;
  el.innerHTML = `
    <div class="msg-avatar">⚠️</div>
    <div class="bubble-wrap">
      <div class="bubble" style="border-color:#fca5a5;background:#fff7f7;">
        <strong style="color:#dc2626;">Connection Error</strong><br/>
        Could not reach the FarmAI backend. Please ensure the server is running.<br/>
        <small style="color:var(--text-light)">${escHtml(errText)}</small><br/><br/>
        📞 Kisan Call Centre: <strong>1800-180-1551</strong> (toll-free)
      </div>
    </div>
  `;
  document.getElementById('messagesContainer').appendChild(el);
  scrollToBottom();
  return id;
}

function askSource(title) {
  document.getElementById('queryInput').value = `Tell me more about: ${title}`;
  sendQuery();
}

function formatAnswer(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>');
}

// ─── Schemes ───────────────────────────────────────────────────────
async function loadSchemes() {
  const panel = document.getElementById('schemesPanel');
  const body  = document.getElementById('schemesBody');
  panel.classList.add('visible');
  body.innerHTML = '<p style="color:var(--text-light);font-size:0.85rem">⏳ Loading schemes…</p>';

  try {
    const res  = await fetch(`${API_BASE}/api/schemes?lang=${currentLang}`);
    const data = await res.json();
    body.innerHTML = data.schemes.map(s => `
      <div class="scheme-card" onclick="askScheme('${escHtml(s.title)}')">
        <div class="scheme-title">🏛️ ${escHtml(s.title)}</div>
        <div class="scheme-summary">${escHtml(s.summary)}</div>
      </div>
    `).join('');
  } catch {
    body.innerHTML = '<p style="color:#dc2626">Failed to load schemes. Check connection.</p>';
  }
}

function closeSchemes() {
  document.getElementById('schemesPanel').classList.remove('visible');
}

function askScheme(title) {
  closeSchemes();
  document.getElementById('queryInput').value = `Tell me about: ${title}`;
  sendQuery();
}

// ─── Voice Input ───────────────────────────────────────────────────
function initVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    document.getElementById('voiceBtn').style.display = 'none';
    return;
  }
  recognition = new SpeechRecognition();
  recognition.continuous    = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    document.getElementById('queryInput').value = transcript;
    stopVoice();
  };
  recognition.onerror = () => stopVoice();
  recognition.onend   = () => stopVoice();
}

function toggleVoice() {
  if (!recognition) { showToast('Voice input not supported in this browser.'); return; }
  if (isListening) {
    recognition.stop();
    stopVoice();
  } else {
    const langMap = { hi:'hi-IN', te:'te-IN', ta:'ta-IN', kn:'kn-IN', mr:'mr-IN', bn:'bn-IN', gu:'gu-IN', pa:'pa-IN', ml:'ml-IN', en:'en-IN' };
    recognition.lang = langMap[currentLang] || 'en-IN';
    recognition.start();
    isListening = true;
    document.getElementById('voiceBtn').classList.add('listening');
    document.getElementById('voiceBtn').title = 'Listening… click to stop';
    showToast('🎙️ Listening… speak your question');
  }
}

function stopVoice() {
  isListening = false;
  const btn = document.getElementById('voiceBtn');
  btn.classList.remove('listening');
  btn.title = 'Voice input';
}

// ─── Toast ─────────────────────────────────────────────────────────
let toastTimer = null;
function showToast(msg, duration = 3000) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), duration);
}

// ─── Utilities ─────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function removeElement(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollToBottom() {
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}
