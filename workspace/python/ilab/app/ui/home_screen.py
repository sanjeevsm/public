from typing import Callable

import customtkinter as ctk

from .. import theme
from ..theme import F
from ..config import get_config

_PROVIDERS = [
    ("Claude (Anthropic)",   "claude",
     ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]),
    ("OpenAI / Copilot",     "openai",
     ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview", "o1-mini"]),
    ("Google Gemini",        "gemini",
     ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"]),
    ("Groq  [FREE]",         "groq",
     ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]),
    ("Ollama  [LOCAL FREE]", "ollama",
     ["llama3.2", "llama3.1", "mistral", "gemma2", "phi3"]),
    ("xAI Grok",             "xai",
     ["grok-3-mini", "grok-3", "grok-3-mini-fast", "grok-3-fast", "grok-2"]),
]
_TAB_NAMES = {
    "claude": "Claude", "openai": "OpenAI", "gemini": "Gemini",
    "groq": "Groq", "ollama": "Ollama", "xai": "xAI",
}
_PROVIDER_HINTS = {
    "groq":   ("FREE tier — get your key at console.groq.com",      "teal"),
    "ollama": ("LOCAL — no key needed.  Run: ollama pull llama3.2",  "teal"),
    "xai":    ("Get your key + free credits at console.x.ai → Billing","teal"),
}
_EXP_LEVELS = ["junior", "mid", "senior", "lead", "architect"]


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, on_start: Callable, on_save: Callable):
        T = theme.get()
        super().__init__(parent, fg_color=T["bg_root"])
        self.on_start = on_start
        self.on_save = on_save
        self.cfg = get_config()
        self._entries: dict[str, dict] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._build_brand_panel(T)
        self._build_settings_panel(T)

    # ── Left panel ────────────────────────────────────────────────────────────

    def _build_brand_panel(self, T):
        card = ctk.CTkFrame(
            self, fg_color=T["bg_card"], corner_radius=24,
            border_width=2, border_color=T["border"],
        )
        card.grid(row=0, column=0, padx=(40, 12), pady=40, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            card, text="iLab+",
            font=ctk.CTkFont(size=F["brand"], weight="bold"),
            text_color=T["accent"],
        ).grid(row=0, column=0, pady=(50, 2))

        ctk.CTkLabel(
            card, text="AI-Powered Interview Simulator",
            font=ctk.CTkFont(size=F["h2"]), text_color=T["text_sub"],
        ).grid(row=1, column=0, pady=(0, 6))

        pill_frame = ctk.CTkFrame(card, fg_color="transparent")
        pill_frame.grid(row=2, column=0, pady=(4, 32))

        pills = [
            ("  Analyze JD with AI  ",       T["cats"][0][1], T["cats"][0][0]),
            ("  Adaptive Questions  ",        T["cats"][1][1], T["cats"][1][0]),
            ("  Instant Feedback  ",          T["cats"][2][1], T["cats"][2][0]),
            ("  Back / Next / Bookmark  ",    T["cats"][3][1], T["cats"][3][0]),
            ("  Performance Report  ",        T["cats"][4][1], T["cats"][4][0]),
        ]
        for i, (text, bg, fg) in enumerate(pills):
            ctk.CTkLabel(
                pill_frame, text=text,
                font=ctk.CTkFont(size=F["small"]),
                text_color=fg, fg_color=bg, corner_radius=8,
            ).grid(row=0, column=i, padx=5)

        ctk.CTkButton(
            card, text="Start Interview",
            font=ctk.CTkFont(size=F["ui"], weight="bold"),
            width=240, height=56, corner_radius=14,
            fg_color=T["accent"], hover_color=T["acc_hov"],
            command=self.on_start,
        ).grid(row=3, column=0, pady=(0, 50))

    # ── Right panel ───────────────────────────────────────────────────────────

    def _build_settings_panel(self, T):
        outer = ctk.CTkFrame(
            self, fg_color=T["bg_card"], corner_radius=24,
            border_width=2, border_color=T["border"],
        )
        outer.grid(row=0, column=1, padx=(12, 40), pady=40, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            scroll, text="Settings",
            font=ctk.CTkFont(size=F["h1"], weight="bold"),
            text_color=T["accent"],
        ).grid(row=0, column=0, sticky="w", pady=(0, 16))

        # ── Appearance ────────────────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="Appearance",
            font=ctk.CTkFont(size=F["h2"], weight="bold"),
            text_color=T["text"],
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        af = ctk.CTkFrame(scroll, fg_color=T["bg_header"], corner_radius=12,
                          border_width=1, border_color=T["border"])
        af.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        af.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            af, text="Theme",
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["text"],
        ).grid(row=0, column=0, padx=16, pady=14, sticky="w")

        self._theme_var = ctk.StringVar(
            value=self.cfg.get("appearance_mode", "dark").title()
        )
        ctk.CTkSegmentedButton(
            af, values=["Dark", "Light"],
            variable=self._theme_var,
            width=180, height=32,
            font=ctk.CTkFont(size=F["label"]),
        ).grid(row=0, column=1, padx=16, pady=14, sticky="w")

        # ── Active AI Provider ────────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="Active AI Provider",
            font=ctk.CTkFont(size=F["h2"], weight="bold"),
            text_color=T["text"],
        ).grid(row=3, column=0, sticky="w", pady=(0, 6))

        self._prov_var = ctk.StringVar(value=self.cfg.ai_provider)
        pr = ctk.CTkFrame(scroll, fg_color=T["bg_header"], corner_radius=12,
                          border_width=1, border_color=T["border"])
        pr.grid(row=4, column=0, sticky="ew", pady=(0, 16))
        pr.grid_columnconfigure(tuple(range(len(_PROVIDERS))), weight=1)

        for i, (label, pid, _) in enumerate(_PROVIDERS):
            ctk.CTkRadioButton(
                pr, text=label, variable=self._prov_var, value=pid,
                command=self._sync_tab,
                font=ctk.CTkFont(size=F["small"]),
                text_color=T["text"],
            ).grid(row=0, column=i, padx=8, pady=14)

        # ── Provider Configuration ────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="Provider Configuration",
            font=ctk.CTkFont(size=F["h2"], weight="bold"),
            text_color=T["text"],
        ).grid(row=5, column=0, sticky="w", pady=(0, 6))

        self._tabs = ctk.CTkTabview(scroll, height=220, fg_color=T["bg_header"])
        self._tabs.grid(row=6, column=0, sticky="ew", pady=(0, 16))

        for label, pid, models in _PROVIDERS:
            tab_name = _TAB_NAMES[pid]
            self._tabs.add(tab_name)
            tab = self._tabs.tab(tab_name)
            tab.grid_columnconfigure(0, weight=1)
            self._build_provider_tab(tab, pid, models, T)

        self._sync_tab()

        # ── Default Quiz Settings ─────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="Default Quiz Settings",
            font=ctk.CTkFont(size=F["h2"], weight="bold"),
            text_color=T["text"],
        ).grid(row=7, column=0, sticky="w", pady=(0, 6))

        qf = ctk.CTkFrame(scroll, fg_color=T["bg_header"], corner_radius=12,
                          border_width=1, border_color=T["border"])
        qf.grid(row=8, column=0, sticky="ew", pady=(0, 16))
        qf.grid_columnconfigure(0, weight=1)

        saved_num = max(5, min(100, round(self.cfg.num_questions / 5) * 5))
        self._num_var = ctk.IntVar(value=saved_num)

        saved_exp = self.cfg.experience_level
        exp_idx = _EXP_LEVELS.index(saved_exp) if saved_exp in _EXP_LEVELS else 1
        self._exp_var = ctk.IntVar(value=exp_idx)

        self._build_num_slider(qf, T)
        self._build_exp_slider(qf, T)

        # ── Save ──────────────────────────────────────────────────────────────
        ctk.CTkButton(
            scroll, text="Save Settings",
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            width=160, height=40, corner_radius=10,
            fg_color=T["accent"], hover_color=T["acc_hov"],
            command=self._save,
        ).grid(row=9, column=0, sticky="e", pady=(0, 4))

    # ── Slider builders ───────────────────────────────────────────────────────

    def _build_num_slider(self, parent, T):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        f.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(f, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text="Number of Questions",
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["text"],
        ).grid(row=0, column=0, sticky="w")

        self._num_lbl = ctk.CTkLabel(
            hdr, text=str(self._num_var.get()),
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["accent"], width=36, anchor="e",
        )
        self._num_lbl.grid(row=0, column=1, sticky="e")

        ctk.CTkSlider(
            f, from_=5, to=100, number_of_steps=19,
            variable=self._num_var,
            button_color=T["accent"], button_hover_color=T["acc_hov"],
            progress_color=T["accent"],
            command=self._on_num_change,
        ).grid(row=1, column=0, sticky="ew", pady=(6, 2))

        rng = ctk.CTkFrame(f, fg_color="transparent")
        rng.grid(row=2, column=0, sticky="ew")
        rng.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(rng, text="5",
                     font=ctk.CTkFont(size=F["small"]), text_color=T["text_mute"],
                     ).grid(row=0, column=0)
        ctk.CTkLabel(rng, text="100",
                     font=ctk.CTkFont(size=F["small"]), text_color=T["text_mute"],
                     ).grid(row=0, column=2)

    def _build_exp_slider(self, parent, T):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 16))
        f.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(f, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text="Experience Level",
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["text"],
        ).grid(row=0, column=0, sticky="w")

        self._exp_lbl = ctk.CTkLabel(
            hdr, text=_EXP_LEVELS[self._exp_var.get()],
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["accent"], width=72, anchor="e",
        )
        self._exp_lbl.grid(row=0, column=1, sticky="e")

        ctk.CTkSlider(
            f, from_=0, to=4, number_of_steps=4,
            variable=self._exp_var,
            button_color=T["accent"], button_hover_color=T["acc_hov"],
            progress_color=T["accent"],
            command=self._on_exp_change,
        ).grid(row=1, column=0, sticky="ew", pady=(6, 2))

        ticks = ctk.CTkFrame(f, fg_color="transparent")
        ticks.grid(row=2, column=0, sticky="ew")
        ticks.grid_columnconfigure(tuple(range(len(_EXP_LEVELS))), weight=1)
        for i, lvl in enumerate(_EXP_LEVELS):
            ctk.CTkLabel(
                ticks, text=lvl,
                font=ctk.CTkFont(size=F["small"]), text_color=T["text_mute"],
                anchor="center",
            ).grid(row=0, column=i, sticky="ew")

    # ── Provider tab builder ──────────────────────────────────────────────────

    def _build_provider_tab(self, tab, pid: str, models: list, T):
        p = self.cfg.get_provider_config(pid)

        if pid in _PROVIDER_HINTS:
            hint_text, hint_key = _PROVIDER_HINTS[pid]
            ctk.CTkLabel(
                tab, text=hint_text,
                font=ctk.CTkFont(size=F["small"]),
                text_color=T[hint_key],
            ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 0))

        r = 2 if pid in _PROVIDER_HINTS else 0

        ctk.CTkLabel(
            tab, text="API Key",
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["text"],
        ).grid(row=r, column=0, sticky="w", padx=14, pady=(12, 4))

        key_entry = ctk.CTkEntry(
            tab, show="*",
            placeholder_text="Paste your API key here…",
            font=ctk.CTkFont(size=F["label"]),
        )
        key_entry.grid(row=r + 1, column=0, sticky="ew", padx=14)
        stored_key = p.get("api_key", "")
        if stored_key and pid != "ollama":
            key_entry.insert(0, stored_key)

        ctk.CTkLabel(
            tab, text="Model",
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["text"],
        ).grid(row=r + 2, column=0, sticky="w", padx=14, pady=(12, 4))

        model_var = ctk.StringVar(value=p.get("model", models[0]))
        ctk.CTkComboBox(
            tab, values=models, variable=model_var,
            font=ctk.CTkFont(size=F["label"]),
        ).grid(row=r + 3, column=0, sticky="ew", padx=14)

        ctk.CTkLabel(
            tab, text="Base URL  (optional — custom endpoints / Azure / proxies)",
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            text_color=T["text"],
        ).grid(row=r + 4, column=0, sticky="w", padx=14, pady=(12, 4))

        url_entry = ctk.CTkEntry(
            tab,
            placeholder_text="https://…  (leave blank for default)",
            font=ctk.CTkFont(size=F["label"]),
        )
        url_entry.grid(row=r + 5, column=0, sticky="ew", padx=14, pady=(0, 14))
        if p.get("base_url"):
            url_entry.insert(0, p["base_url"])

        self._entries[pid] = {
            "api_key":   key_entry,
            "model_var": model_var,
            "base_url":  url_entry,
        }

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_num_change(self, val):
        rounded = max(5, min(100, round(float(val) / 5) * 5))
        self._num_lbl.configure(text=str(rounded))

    def _on_exp_change(self, val):
        idx = max(0, min(4, round(float(val))))
        self._exp_lbl.configure(text=_EXP_LEVELS[idx])

    def _sync_tab(self):
        pid = self._prov_var.get()
        name = _TAB_NAMES.get(pid, "Claude")
        try:
            self._tabs.set(name)
        except Exception:
            pass

    def _save(self):
        self.cfg.set("ai_provider", self._prov_var.get())
        self.cfg.set("appearance_mode", self._theme_var.get().lower())

        for pid, e in self._entries.items():
            self.cfg.set_provider_config(pid, "api_key",  e["api_key"].get().strip())
            self.cfg.set_provider_config(pid, "model",    e["model_var"].get().strip())
            self.cfg.set_provider_config(pid, "base_url", e["base_url"].get().strip())

        raw_num = float(self._num_var.get())
        self.cfg.set("num_questions", max(5, min(100, round(raw_num / 5) * 5)))

        exp_idx = max(0, min(4, round(float(self._exp_var.get()))))
        self.cfg.set("experience_level", _EXP_LEVELS[exp_idx])

        self.cfg.save()
        theme.set_mode(self._theme_var.get().lower())
        self.on_save()
