/* Loading page — SSE status + polling + meta-refresh fallback */

function startLoading(jobId) {

  /* ── DOM refs ────────────────────────────────────────── */
  const statusEl  = document.getElementById("status-text");
  const errorEl   = document.getElementById("error-msg");
  const barEl     = document.querySelector(".progress-inner-anim");
  const backLink  = document.getElementById("back-link");
  const cancelBtn = document.getElementById("cancel-btn");
  const elapsedEl = document.getElementById("elapsed-text");
  const tipEl     = document.getElementById("tip-text");

  /* ── Mutable state ───────────────────────────────────── */
  let navigated  = false;
  let startTime  = Date.now();
  let sseSource  = null;   // assigned after definition so goToQuiz can close it
  let elapsedTmr = null;
  let pollTmr    = null;

  /* ── Step helpers ────────────────────────────────────── */
  function setStep(id, state) {
    const el = document.getElementById("step-" + id);
    if (!el) return;
    el.className = "gen-step gen-step-" + state;
    const icon = el.querySelector(".step-icon");
    if (icon) icon.textContent =
      state === "done"   ? "\u2713" :
      state === "active" ? "\u25CF" : "\u25CB";
  }

  function applySteps(status) {
    const s = (status || "").toLowerCase();
    if (s.includes("connecting")) {
      setStep("connect","active"); setStep("analyze","pending");
      setStep("generate","pending"); setStep("finalize","pending");
    } else if (s.includes("analyzing")||s.includes("analysing")||s.includes("crafting")) {
      setStep("connect","done");   setStep("analyze","active");
      setStep("generate","pending"); setStep("finalize","pending");
    } else if (s.includes("generated")||s.includes("questions successfully")) {
      setStep("connect","done");   setStep("analyze","done");
      setStep("generate","done");  setStep("finalize","active");
    }
  }

  function markAllDone() {
    ["connect","analyze","generate","finalize"].forEach(id => setStep(id,"done"));
  }

  /* ── Elapsed timer + tips ────────────────────────────── */
  const TIPS = [
    [ 8, "AI models typically take 15\u201330s to craft good questions."],
    [25, "Generating detailed explanations for each answer\u2026"],
    [45, "Complex roles require more thorough question crafting."],
    [70, "Still working \u2014 thank you for your patience."],
  ];

  elapsedTmr = setInterval(() => {
    const secs = Math.floor((Date.now() - startTime) / 1000);
    const m = Math.floor(secs / 60), s = secs % 60;
    if (elapsedEl) elapsedEl.textContent = m > 0 ? `${m}m ${s}s elapsed` : `${secs}s elapsed`;
    const tip = TIPS.filter(([t]) => secs >= t).pop();
    if (tip && tipEl) tipEl.textContent = tip[1];
  }, 1000);

  /* ── Navigation ──────────────────────────────────────── */
  function goToQuiz(url) {
    if (navigated || !url) return;
    navigated = true;
    url = url.trim();

    // Stop all timers
    clearInterval(elapsedTmr);
    clearInterval(pollTmr);

    // *** Critical: close the SSE connection BEFORE navigating.
    // Browsers can block window.location changes while a streaming
    // (EventSource) connection is still active on the same page.
    if (sseSource) {
      try { sseSource.close(); } catch (_) {}
      sseSource = null;
    }

    markAllDone();
    if (statusEl) statusEl.textContent = "Questions ready! Loading quiz\u2026";

    // Show the link so the user can click immediately if needed
    if (backLink) {
      backLink.href         = url;
      backLink.textContent  = "\u25b6 Open Quiz";
      backLink.className    = "btn btn-primary btn-lg";
      backLink.style.display = "inline-flex";
    }

    // Wait 200 ms for the SSE connection to fully close, then navigate.
    // The <meta http-equiv="refresh"> in the page head is a final safety net:
    // it reloads /loading/<job_id> every 3 s, and the server 302-redirects
    // to the quiz once the job is done — no JS required.
    setTimeout(() => { window.location.href = url; }, 200);
  }

  /* ── Error display ───────────────────────────────────── */
  function showError(msg) {
    clearInterval(elapsedTmr);
    clearInterval(pollTmr);
    if (barEl)     barEl.style.display     = "none";
    if (cancelBtn) cancelBtn.style.display = "none";
    if (statusEl)  { statusEl.style.color  = "var(--red)"; statusEl.textContent = ""; }
    if (errorEl)   { errorEl.textContent   = msg; errorEl.style.display = "block"; }
    if (backLink)  { backLink.textContent  = "\u2190 Back"; backLink.style.display = "inline-flex"; }
  }

  /* ── SSE — real-time status display ─────────────────── */
  sseSource = new EventSource("/stream/" + jobId);

  sseSource.addEventListener("status", (e) => {
    if (navigated) return;
    if (statusEl) statusEl.textContent = e.data;
    applySteps(e.data);
  });

  sseSource.addEventListener("done", (e) => {
    // sseSource will be closed inside goToQuiz
    goToQuiz(e.data);
  });

  sseSource.addEventListener("error", (e) => {
    if (navigated) return;
    if (sseSource) { try { sseSource.close(); } catch(_){} sseSource = null; }
    showError(e.data || "Generation failed. Please try again.");
  });

  sseSource.onerror = () => {
    if (navigated) return;
    // Don't show an error yet — polling will catch the real outcome
  };

  /* ── Polling — reliable navigation trigger ───────────── */
  pollTmr = setInterval(async () => {
    if (navigated) { clearInterval(pollTmr); return; }
    try {
      const resp = await fetch("/api/status/" + jobId);
      if (!resp.ok) return;
      const data = await resp.json();
      if (!data.done) {
        if (data.status && !navigated) {
          if (statusEl) statusEl.textContent = data.status;
          applySteps(data.status);
        }
        return;
      }
      clearInterval(pollTmr);
      if (data.error) showError(data.error);
      else            goToQuiz(data.quiz_url);
    } catch (_) { /* transient network error — retry */ }
  }, 800);

  // Mark first step active immediately
  setStep("connect", "active");
}
