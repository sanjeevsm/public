import hashlib
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))


class TTLStore:
    """Thread-safe in-memory dict with TTL expiry and background cleanup.

    Access refreshes the TTL so active jobs stay alive.
    Items expire after `ttl` seconds of inactivity (default 2 hours).
    A background daemon thread purges expired entries every 5 minutes.
    """

    def __init__(self, ttl: int = 7200):
        self._data: dict = {}
        self._ts: dict = {}
        self._lock = threading.Lock()
        self._ttl = ttl
        t = threading.Thread(target=self._cleaner, daemon=True)
        t.start()

    def _alive(self, key: str) -> bool:
        return key in self._data and (time.time() - self._ts.get(key, 0)) < self._ttl

    def _cleaner(self):
        while True:
            time.sleep(300)
            now = time.time()
            with self._lock:
                expired = [k for k, ts in self._ts.items() if now - ts >= self._ttl]
                for k in expired:
                    self._data.pop(k, None)
                    self._ts.pop(k, None)

    # dict-compatible interface -----------------------------------------------

    def get(self, key: str, default=None):
        with self._lock:
            if not self._alive(key):
                return default
            self._ts[key] = time.time()
            return self._data[key]

    def __setitem__(self, key: str, value):
        with self._lock:
            self._data[key] = value
            self._ts[key] = time.time()

    def __getitem__(self, key: str):
        with self._lock:
            if not self._alive(key):
                raise KeyError(key)
            self._ts[key] = time.time()
            return self._data[key]

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return self._alive(key)

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
    # ── Light themes ─────────────────────────────────────
    {
        "id":      "ocean",
        "label":   "Ocean",
        "bg":      "#f0f8ff",
        "accent":  "#0284c7",
    },
    {
        "id":      "rose",
        "label":   "Rose",
        "bg":      "#fff5f5",
        "accent":  "#e11d48",
    },
    {
        "id":      "sage",
        "label":   "Sage",
        "bg":      "#f0faf4",
        "accent":  "#059669",
    },
    {
        "id":      "sunset",
        "label":   "Sunset",
        "bg":      "#fffbf0",
        "accent":  "#ea580c",
    },
    {
        "id":      "lavender",
        "label":   "Lavender",
        "bg":      "#f8f5ff",
        "accent":  "#7c3aed",
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
    secret = os.environ.get("ILAB_SECRET", "")
    if not secret:
        import secrets as _secrets
        secret = _secrets.token_hex(32)
    app.secret_key = secret

    # TTL-backed in-memory stores (auto-expire after 2 h, purged every 5 min)
    app.jobs    = TTLStore()   # job_id    → {status, questions, error, done}
    app.quizzes = TTLStore()   # quiz_id   → {questions, answers}
    app.results = TTLStore()   # result_id → {questions, answers}

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
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    host  = os.environ.get("HOST", "0.0.0.0")
    port  = int(os.environ.get("PORT", 8000))
    flask_app.run(debug=debug, host=host, port=port, threaded=True)
