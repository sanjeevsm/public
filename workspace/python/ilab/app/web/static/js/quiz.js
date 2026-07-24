/* Quiz page — state machine */
/* globals: QUESTIONS, QUIZ_ID (set via <script> in quiz.html) */

const LETTERS = ["A", "B", "C", "D"];

const state = {
  idx: 0,
  answers: {},       // { questionIdx (number): optionIdx (number | null) }
  bookmarks: new Set(),
  filterBm: false,
};

// ── helpers ───────────────────────────────────────────────────────────────────

function getNavIndices() {
  const all = QUESTIONS.map((_, i) => i);
  return state.filterBm && state.bookmarks.size > 0
    ? all.filter((i) => state.bookmarks.has(i))
    : all;
}

function qs(id) { return document.getElementById(id); }

// ── rendering ─────────────────────────────────────────────────────────────────

function renderQuestion(idx) {
  state.idx = idx;
  const q   = QUESTIONS[idx];

  qs("question-text").textContent = q.text;
  qs("q-number").textContent      = `Q${idx + 1} / ${QUESTIONS.length}`;
  qs("q-category").textContent    = q.category || "General";
  qs("q-category").setAttribute("style", catStyle(q.category || "General"));

  const diffBadge = qs("q-difficulty");
  diffBadge.textContent       = q.difficulty;
  diffBadge.setAttribute("data-d", q.difficulty);
  diffBadge.className         = "badge badge-diff";

  const answered = state.answers[idx] !== undefined;
  const selected = state.answers[idx] ?? null;

  // options
  const container = qs("options-container");
  container.innerHTML = "";
  q.options.forEach((opt, j) => {
    const div    = document.createElement("div");
    div.className = "option-card";
    div.dataset.pos = j;

    if (answered) {
      div.classList.add("locked");
      if (j === q.correct_index)                div.classList.add("correct");
      else if (j === selected)                  div.classList.add("wrong");
    } else {
      div.addEventListener("click", () => pickAnswer(idx, j));
    }

    const letter  = document.createElement("span");
    letter.className = "option-letter";
    letter.textContent = LETTERS[j];

    const text    = document.createElement("span");
    text.className = "option-text";
    text.textContent = opt;

    div.appendChild(letter);
    div.appendChild(text);
    container.appendChild(div);
  });

  // explanation
  const expDiv = qs("explanation");
  if (answered) {
    const correct = selected === q.correct_index;
    expDiv.innerHTML = `
      <span class="exp-icon ${correct ? "correct" : "incorrect"}">${correct ? "✓" : "✗"}</span>
      <span class="exp-text"><strong>${correct ? "Correct!" : "Incorrect."}</strong> ${q.explanation || ""}</span>
    `;
    expDiv.style.display = "flex";
  } else {
    expDiv.style.display = "none";
  }

  // bookmark button
  const bmBtn = qs("bookmark-btn");
  const isBm  = state.bookmarks.has(idx);
  bmBtn.textContent = isBm ? "★" : "☆";
  bmBtn.className   = "bookmark-btn" + (isBm ? " bookmarked" : "");

  // nav buttons
  const nav     = getNavIndices();
  const pos     = nav.indexOf(idx);
  const isLast  = pos === nav.length - 1;
  const isFirst = pos === 0;

  qs("next-btn").style.display   = isLast  ? "none"  : "inline-flex";
  qs("finish-btn").style.display = isLast  ? "inline-flex" : "none";
  qs("back-btn").disabled        = isFirst;

  renderNavRail();
  renderProgress();
}

function renderNavRail() {
  const rail = qs("nav-rail");
  rail.innerHTML = "";
  getNavIndices().forEach((i) => {
    const btn = document.createElement("button");
    btn.className  = "nav-dot";
    btn.title      = `Q${i + 1}`;

    const ans = state.answers[i];
    if (i === state.idx)                          btn.classList.add("current");
    if (state.bookmarks.has(i))                   btn.classList.add("bookmarked");
    if (ans !== undefined && ans !== null) {
      if (QUESTIONS[i].correct_index === ans)      btn.classList.add("answered-ok");
      else                                         btn.classList.add("answered-wrong");
    }

    btn.textContent = state.bookmarks.has(i) ? "★" : (i + 1);
    btn.addEventListener("click", () => renderQuestion(i));
    rail.appendChild(btn);
  });

  // scroll active dot into view
  const current = rail.querySelector(".current");
  if (current) current.scrollIntoView({ inline: "nearest", block: "nearest" });
}

function renderProgress() {
  qs("progress-text").textContent = `Question ${state.idx + 1} of ${QUESTIONS.length}`;
}

// stable category colour (mirrors flask_app.py cat_style filter)
const _CAT_PALETTES = [
  ["#1e1f3b","#818cf8"],["#1e2a3b","#60a5fa"],["#0f2e2e","#2dd4bf"],
  ["#2e2a0f","#fbbf24"],["#2e1515","#f87171"],["#2a1e3b","#c084fc"],
  ["#0f2e1a","#4ade80"],["#2e1e2a","#f472b6"],
];
function catStyle(cat) {
  let hash = 0;
  for (let i = 0; i < cat.length; i++) hash = (hash * 31 + cat.charCodeAt(i)) >>> 0;
  const [bg, color] = _CAT_PALETTES[hash % _CAT_PALETTES.length];
  return `background:${bg};color:${color};border:1px solid ${color}33`;
}

// ── actions ───────────────────────────────────────────────────────────────────

function pickAnswer(qIdx, optIdx) {
  state.answers[qIdx] = optIdx;
  fetch("/quiz/answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ quiz_id: QUIZ_ID, question_idx: qIdx, answer_idx: optIdx }),
  });
  renderQuestion(qIdx);
}

window.navBack = function () {
  const nav = getNavIndices();
  const pos = nav.indexOf(state.idx);
  if (pos > 0) renderQuestion(nav[pos - 1]);
};

window.navNext = function () {
  const nav = getNavIndices();
  const pos = nav.indexOf(state.idx);
  if (pos < nav.length - 1) renderQuestion(nav[pos + 1]);
};

window.toggleBookmark = function () {
  const idx = state.idx;
  if (state.bookmarks.has(idx)) state.bookmarks.delete(idx);
  else                           state.bookmarks.add(idx);
  _refreshBmBtn();
  renderQuestion(idx);
};

window.toggleBmFilter = function () {
  state.filterBm = !state.filterBm;
  _refreshBmBtn();
  const nav = getNavIndices();
  if (nav.length > 0 && !nav.includes(state.idx)) renderQuestion(nav[0]);
  else renderNavRail();
};

function _refreshBmBtn() {
  const btn  = qs("filter-bm-btn");
  const count = state.bookmarks.size;
  btn.textContent  = count > 0 ? `★ Bookmarks (${count})` : "☆ Bookmarks";
  btn.className    = "btn btn-ghost" + (state.filterBm ? " active-filter" : "");
}

window.finishQuiz = async function () {
  const answers = {};
  for (let i = 0; i < QUESTIONS.length; i++) {
    answers[i] = state.answers[i] !== undefined ? state.answers[i] : null;
  }
  const resp = await fetch("/quiz/finish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ quiz_id: QUIZ_ID, answers }),
  });
  const data = await resp.json();
  window.location.href = data.redirect;
};

// ── init ──────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  renderQuestion(0);
});
