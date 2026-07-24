import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask

BASE = os.path.dirname(__file__)

# Theme definitions — used by the cat_style filter and by templates
THEMES = [
    {
        "id":      "dark-pro",
        "label":   "Dark Pro",
        "bg":      "#0d1117",
        "accent":  "#6366f1",
    },
    {
        "id":      "midnight",
        "label":   "Midnight",
        "bg":      "#080b14",
        "accent":  "#a855f7",
    },
    {
        "id":      "navy",
        "label":   "Navy",
        "bg":      "#0f172a",
        "accent":  "#06b6d4",
    },
    {
        "id":      "forest",
        "label":   "Forest",
        "bg":      "#0b1714",
        "accent":  "#10b981",
    },
    {
        "id":      "light",
        "label":   "Light",
        "bg":      "#f6f8fa",
        "accent":  "#6366f1",
    },
    {
        "id":      "warm",
        "label":   "Warm",
        "bg":      "#120f07",
        "accent":  "#f59e0b",
    },
]

# Badge palettes — rgba so they work on all theme backgrounds
_PALETTES = [
    ("rgba(129,140,248,.15)", "#818cf8"),   # indigo
    ("rgba(96,165,250,.15)",  "#60a5fa"),   # blue
    ("rgba(45,212,191,.15)",  "#2dd4bf"),   # teal
    ("rgba(251,191,36,.15)",  "#fbbf24"),   # amber
    ("rgba(248,113,113,.15)", "#f87171"),   # red
    ("rgba(192,132,252,.15)", "#c084fc"),   # purple
    ("rgba(74,222,128,.15)",  "#4ade80"),   # green
    ("rgba(244,114,182,.15)", "#f472b6"),   # pink
]


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=os.path.join(BASE, "app", "web", "static"),
        template_folder=os.path.join(BASE, "app", "web", "templates"),
    )
    app.secret_key = os.environ.get("ILAB_SECRET", "ilab-dev-secret-key-change-in-prod")

    # In-memory stores (single-process dev server)
    app.jobs    = {}   # job_id    → {status, questions, error, done}
    app.quizzes = {}   # quiz_id   → {questions, answers}
    app.results = {}   # result_id → {questions, answers}

    # ── template filter ───────────────────────────────────────────────────────
    @app.template_filter("cat_style")
    def cat_style(cat: str) -> str:
        idx = int(hashlib.md5((cat or "general").encode()).hexdigest()[:8], 16) % len(_PALETTES)
        bg, color = _PALETTES[idx]
        return f"background:{bg};color:{color};border:1px solid {color}"

    # ── make THEMES list available in every template ───────────────────────
    @app.context_processor
    def _inject_themes():
        return {"THEMES": THEMES}

    # ── blueprint ─────────────────────────────────────────────────────────────
    from app.web.routes import bp
    app.register_blueprint(bp)

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, port=5000, threaded=True)
