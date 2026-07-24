import json
import time
import uuid

from flask import (
    Blueprint, current_app, jsonify, redirect, render_template,
    request, Response, session, url_for,
)

bp = Blueprint("main", __name__)

_LEGACY_THEME_MAP = {"dark": "dark-pro", "light": "light"}

PROVIDER_LABELS = {
    "claude": ("🤖", "Claude"),
    "openai": ("🧠", "OpenAI"),
    "gemini": ("✨", "Gemini"),
    "groq":   ("⚡", "Groq"),
    "ollama": ("🦙", "Ollama"),
    "xai":    ("🚀", "xAI"),
}
ALL_PROVIDERS = list(PROVIDER_LABELS.keys())

PROVIDER_MODELS = {
    "claude":  ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
    "openai":  ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "gemini":  ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
    "groq":    ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"],
    "ollama":  ["llama3.2", "llama3.1", "mistral", "codellama", "qwen2.5"],
    "xai":     ["grok-3-mini", "grok-3", "grok-beta"],
}

EXP_LEVELS  = ["junior", "mid", "senior", "lead", "architect"]
QUESTION_COUNTS = [5, 10, 15, 20, 25, 30, 40, 50]


# ── context processors ────────────────────────────────────────────────────────

@bp.app_context_processor
def _inject_theme():
    from app.config import get_config
    cfg   = get_config()
    raw   = cfg.get("appearance_mode", "dark-pro")
    theme = _LEGACY_THEME_MAP.get(raw, raw)
    return {"theme": theme}


def _model_status(cfg):
    """Return a dict describing the active provider/model status for templates."""
    active   = cfg.ai_provider
    pcfg     = cfg.get_provider_config(active)
    api_key  = (pcfg.get("api_key") or "").strip()
    model    = pcfg.get("model") or ""
    emoji, label = PROVIDER_LABELS.get(active, ("🤖", active.capitalize()))

    # Ollama is local — no key needed
    has_key = bool(api_key) or active == "ollama"

    # Check whether ANY provider has a key at all
    any_configured = any(
        (cfg.get_provider_config(p).get("api_key") or "").strip() or p == "ollama"
        for p in ALL_PROVIDERS
    )

    if not any_configured:
        status = "error"
        title  = "No AI provider configured"
        sub    = "Add an API key in Settings to start generating questions."
    elif not has_key:
        status = "warning"
        title  = f"No API key for {label}"
        sub    = f"The active provider is {label} but no API key is set. Change provider or add a key in Settings."
    else:
        status = "ok"
        title  = f"{emoji} {label} — {model}"
        sub    = None

    return {
        "status": status,
        "title":  title,
        "sub":    sub,
        "emoji":  emoji,
        "label":  label,
        "model":  model,
    }


# ── home (start interview) ────────────────────────────────────────────────────

@bp.route("/")
def home():
    from app.config import get_config
    cfg = get_config()
    return render_template(
        "home.html",
        cfg=cfg,
        model_status=_model_status(cfg),
        exp_levels=EXP_LEVELS,
        question_counts=QUESTION_COUNTS,
    )


# ── settings page ─────────────────────────────────────────────────────────────

@bp.route("/settings")
def settings_page():
    from app.config import get_config
    cfg = get_config()
    return render_template(
        "settings.html",
        cfg=cfg,
        providers_data=cfg.get("providers", {}),
        models=PROVIDER_MODELS,
        active_provider=cfg.ai_provider,
        exp_levels=EXP_LEVELS,
        question_counts=QUESTION_COUNTS,
    )


@bp.route("/settings", methods=["POST"])
def save_settings():
    from app.config import get_config
    cfg = get_config()

    cfg.set("ai_provider",     request.form.get("ai_provider", "claude"))
    cfg.set("appearance_mode", request.form.get("appearance_mode", "dark-pro"))
    cfg.set("num_questions",   int(request.form.get("num_questions", 10)))
    cfg.set("experience_level", request.form.get("experience_level", "mid"))

    for p in ALL_PROVIDERS:
        cfg.set_provider_config(p, "api_key",  request.form.get(f"{p}_api_key",  ""))
        cfg.set_provider_config(p, "model",    request.form.get(f"{p}_model",    ""))
        cfg.set_provider_config(p, "base_url", request.form.get(f"{p}_base_url", ""))

    cfg.save()
    return redirect(url_for("main.settings_page") + "?saved=1")


# ── redirect legacy /setup ────────────────────────────────────────────────────

@bp.route("/setup")
def setup():
    return redirect(url_for("main.home"))


# ── generate ─────────────────────────────────────────────────────────────────

@bp.route("/generate", methods=["POST"])
def generate():
    from app.config import get_config
    from app.services.question_generator import QuestionGenerator

    text = request.form.get("text", "").strip()
    mode = request.form.get("mode", "jd")
    exp  = request.form.get("experience_level", "mid")
    num  = int(request.form.get("num_questions", 10))

    if not text:
        return redirect(url_for("main.home"))

    cfg = get_config()
    cfg.set("experience_level", exp)
    cfg.set("num_questions",    num)
    cfg.save()

    job_id = str(uuid.uuid4())

    # Capture plain dict references NOW (in request context) so the background
    # thread can safely update them — current_app is a proxy that only works
    # inside the request thread and would raise RuntimeError in a daemon thread.
    jobs_store = current_app.jobs
    jobs_store[job_id] = {
        "status":    "Initialising…",
        "questions": None,
        "error":     None,
        "done":      False,
    }

    def on_success(questions):
        jobs_store[job_id]["questions"] = [
            {
                "text":          q.text,
                "options":       q.options,
                "correct_index": q.correct_index,
                "explanation":   q.explanation,
                "category":      q.category,
                "difficulty":    q.difficulty,
            }
            for q in questions
        ]
        jobs_store[job_id]["done"] = True

    def on_error(exc):
        jobs_store[job_id]["error"] = str(exc)
        jobs_store[job_id]["done"]  = True

    def on_progress(msg):
        jobs_store[job_id]["status"] = msg

    QuestionGenerator().generate_async(
        text, exp, num, on_success, on_error, on_progress, mode=mode
    )

    return redirect(url_for("main.loading", job_id=job_id))


# ── loading + SSE ─────────────────────────────────────────────────────────────

@bp.route("/loading/<job_id>")
def loading(job_id):
    from app.config import get_config
    cfg = get_config()
    job = current_app.jobs.get(job_id)

    # Fast-path: if the page is reloaded (e.g. via meta-refresh) and the job
    # is already done, redirect straight to the quiz — no JS needed.
    if job and job.get("done") and not job.get("error"):
        quiz_url = job.get("quiz_url")
        if not quiz_url:
            quiz_id  = str(uuid.uuid4())
            quiz_url = f"/quiz?quiz_id={quiz_id}"
            current_app.quizzes[quiz_id] = {
                "questions": job["questions"],
                "answers":   {},
            }
            job["quiz_url"] = quiz_url
        return redirect(quiz_url)

    return render_template("loading.html", job_id=job_id, cfg=cfg)


@bp.route("/stream/<job_id>")
def stream(job_id):
    from flask import stream_with_context

    # Capture plain dict references here (in request context) — the generator
    # runs in a different context and cannot use current_app safely.
    jobs    = current_app.jobs
    quizzes = current_app.quizzes

    def _sse(event, data):
        return f"event: {event}\ndata: {data}\n\n"

    def generator():
        last_status = None
        tick        = 0

        # Immediately send a comment to establish the stream and flush buffers.
        yield ": connected\n\n"

        for _ in range(600):
            tick += 1

            # Keepalive ping every ~10 seconds so the browser doesn't time out
            # on long-running generations (comment lines are ignored by EventSource).
            if tick % 30 == 0:
                yield ": keepalive\n\n"

            job = jobs.get(job_id)
            if job is None:
                yield _sse("error", "Job not found.")
                return

            if job["status"] != last_status:
                last_status = job["status"]
                yield _sse("status", job["status"])

            if job["done"]:
                if job["error"]:
                    yield _sse("error", job["error"])
                else:
                    quiz_id  = str(uuid.uuid4())
                    quiz_url = f"/quiz?quiz_id={quiz_id}"
                    quizzes[quiz_id] = {
                        "questions": job["questions"],
                        "answers":   {},
                    }
                    # Cache the URL so the polling endpoint can return it too
                    job["quiz_url"] = quiz_url
                    yield _sse("done", quiz_url)
                return

            time.sleep(0.3)

        yield _sse("error", "Request timed out. Please try again.")

    return Response(
        stream_with_context(generator()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":        "keep-alive",
        },
    )


# ── polling status endpoint ───────────────────────────────────────────────────

@bp.route("/api/status/<job_id>")
def job_status(job_id):
    """Polled by loading.js as a reliable navigation trigger."""
    job = current_app.jobs.get(job_id)
    if not job:
        return jsonify({"done": True, "error": "Job not found. Please try again."})

    if not job["done"]:
        return jsonify({"done": False, "status": job.get("status", "Working…")})

    if job.get("error"):
        return jsonify({"done": True, "error": job["error"]})

    # Use the URL the SSE stream already created, or create a fresh one.
    quiz_url = job.get("quiz_url")
    if not quiz_url:
        quiz_id  = str(uuid.uuid4())
        quiz_url = f"/quiz?quiz_id={quiz_id}"
        current_app.quizzes[quiz_id] = {
            "questions": job["questions"],
            "answers":   {},
        }
        job["quiz_url"] = quiz_url

    return jsonify({"done": True, "quiz_url": quiz_url})


# ── quiz ─────────────────────────────────────────────────────────────────────

@bp.route("/quiz")
def quiz():
    quiz_id   = request.args.get("quiz_id") or session.get("quiz_id")
    quiz_data = current_app.quizzes.get(quiz_id) if quiz_id else None
    if not quiz_data:
        return redirect(url_for("main.home"))
    session["quiz_id"] = quiz_id
    return render_template("quiz.html", quiz_id=quiz_id, questions=quiz_data["questions"])


@bp.route("/quiz/answer", methods=["POST"])
def quiz_answer():
    data    = request.get_json() or {}
    quiz_id = data.get("quiz_id") or session.get("quiz_id")
    q_idx   = str(data.get("question_idx", ""))
    a_idx   = data.get("answer_idx")
    quiz_data = current_app.quizzes.get(quiz_id)
    if quiz_data is not None:
        quiz_data["answers"][q_idx] = a_idx
    return jsonify({"ok": True})


@bp.route("/quiz/finish", methods=["POST"])
def quiz_finish():
    data    = request.get_json() or {}
    quiz_id = data.get("quiz_id") or session.get("quiz_id")
    quiz_data = current_app.quizzes.get(quiz_id)
    if not quiz_data:
        return jsonify({"redirect": url_for("main.home")})
    for k, v in (data.get("answers") or {}).items():
        quiz_data["answers"][str(k)] = v
    questions = quiz_data["questions"]
    answers   = [quiz_data["answers"].get(str(i)) for i in range(len(questions))]
    result_id = str(uuid.uuid4())
    current_app.results[result_id] = {"questions": questions, "answers": answers}
    session["result_id"] = result_id
    return jsonify({"redirect": url_for("main.results")})


# ── results ───────────────────────────────────────────────────────────────────

@bp.route("/results")
def results():
    result_id = session.get("result_id")
    result    = current_app.results.get(result_id) if result_id else None
    if not result:
        return redirect(url_for("main.home"))

    questions = result["questions"]
    answers   = result["answers"]
    total     = len(questions)
    correct   = sum(
        1 for i, q in enumerate(questions)
        if answers[i] is not None and answers[i] == q["correct_index"]
    )
    skipped = sum(1 for a in answers if a is None)
    wrong   = total - correct - skipped
    pct     = (correct / total * 100) if total else 0.0

    if pct >= 90:   grade, grade_color = "Outstanding 🏆",       "green"
    elif pct >= 80: grade, grade_color = "Excellent ⭐",           "green"
    elif pct >= 70: grade, grade_color = "Good Job 👍",            "amber"
    elif pct >= 50: grade, grade_color = "Keep Practising 💪",     "amber"
    else:           grade, grade_color = "Needs Improvement 📚",   "red"

    review = []
    for i, q in enumerate(questions):
        ans = answers[i]
        correct_idx = q["correct_index"]
        opts = []
        for j, opt in enumerate(q["options"]):
            if j == correct_idx:             cls = "correct"
            elif ans == j:                   cls = "selected"
            else:                            cls = ""
            opts.append({"letter": "ABCD"[j], "text": opt, "cls": cls})

        outcome = (
            "correct"   if ans is not None and ans == correct_idx else
            "skipped"   if ans is None else
            "incorrect"
        )
        review.append({
            "num": i + 1, "text": q["text"],
            "category": q["category"], "difficulty": q["difficulty"],
            "options": opts, "explanation": q["explanation"], "outcome": outcome,
        })

    return render_template(
        "results.html",
        total=total, correct=correct, wrong=wrong, skipped=skipped,
        pct=pct, grade=grade, grade_color=grade_color, review=review,
    )
