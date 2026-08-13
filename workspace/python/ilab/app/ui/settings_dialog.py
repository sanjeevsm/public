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
]
_TAB_NAMES = {
    "claude": "Claude", "openai": "OpenAI", "gemini": "Gemini",
    "groq": "Groq", "ollama": "Ollama",
}
_PROVIDER_HINTS = {
    "groq":   ("FREE tier — get your key at console.groq.com",      "teal"),
    "ollama": ("LOCAL — no key needed.  Run: ollama pull llama3.2",  "teal"),
}


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        T = theme.get()
        super().__init__(parent)
        self.title("Settings — iLab+")
        self.geometry("780x760")
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=T["bg_root"])

        self.cfg = get_config()
        self._entries: dict[str, dict] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color=T["bg_root"])
        scroll.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="Settings",
                     font=ctk.CTkFont(size=F["h1"] + 4, weight="bold"),
                     text_color=T["accent"],
                     ).grid(row=0, column=0, sticky="w", pady=(0, 18))

        # ── Appearance ────────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Appearance",
                     font=ctk.CTkFont(size=F["h2"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=1, column=0, sticky="w", pady=(0, 8))

        af = ctk.CTkFrame(scroll, fg_color=T["bg_card"], corner_radius=12,
                           border_width=1, border_color=T["border"])
        af.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        af.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(af, text="Theme",
                     font=ctk.CTkFont(size=F["label"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self._theme_var = ctk.StringVar(
            value=self.cfg.get("appearance_mode", "dark").title()
        )
        ctk.CTkSegmentedButton(
            af, values=["Dark", "Light"],
            variable=self._theme_var,
            width=200, height=34,
            font=ctk.CTkFont(size=F["label"]),
        ).grid(row=0, column=1, padx=20, pady=18, sticky="w")

        # ── Provider radio ────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Active AI Provider",
                     font=ctk.CTkFont(size=F["h2"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=3, column=0, sticky="w", pady=(0, 8))

        self._prov_var = ctk.StringVar(value=self.cfg.ai_provider)
        pr = ctk.CTkFrame(scroll, fg_color=T["bg_card"], corner_radius=12,
                           border_width=1, border_color=T["border"])
        pr.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        pr.grid_columnconfigure(tuple(range(len(_PROVIDERS))), weight=1)

        for i, (label, pid, _) in enumerate(_PROVIDERS):
            ctk.CTkRadioButton(
                pr, text=label, variable=self._prov_var, value=pid,
                command=self._sync_tab,
                font=ctk.CTkFont(size=F["small"]),
                text_color=T["text"],
            ).grid(row=0, column=i, padx=10, pady=18)

        # ── Per-provider tabs ─────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Provider Configuration",
                     font=ctk.CTkFont(size=F["h2"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=5, column=0, sticky="w", pady=(0, 8))

        self._tabs = ctk.CTkTabview(scroll, height=240,
                                    fg_color=T["bg_card"])
        self._tabs.grid(row=6, column=0, sticky="ew", pady=(0, 20))

        for label, pid, models in _PROVIDERS:
            tab_name = _TAB_NAMES[pid]
            self._tabs.add(tab_name)
            tab = self._tabs.tab(tab_name)
            tab.grid_columnconfigure(0, weight=1)
            self._build_provider_tab(tab, pid, models, T)

        self._sync_tab()

        # ── Default quiz settings ─────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Default Quiz Settings",
                     font=ctk.CTkFont(size=F["h2"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=7, column=0, sticky="w", pady=(0, 8))

        qf = ctk.CTkFrame(scroll, fg_color=T["bg_card"], corner_radius=12,
                           border_width=1, border_color=T["border"])
        qf.grid(row=8, column=0, sticky="ew", pady=(0, 22))
        qf.grid_columnconfigure((0, 1), weight=1)

        self._num_var = ctk.StringVar(value=str(self.cfg.num_questions))
        self._exp_var = ctk.StringVar(value=self.cfg.experience_level)

        self._setting_combo(qf, col=0, label="Questions",
                            values=["5", "10", "15", "20", "25", "30"],
                            var=self._num_var, T=T)
        self._setting_combo(qf, col=1, label="Experience Level",
                            values=["junior", "mid", "senior", "lead"],
                            var=self._exp_var, T=T)

        # ── Buttons ───────────────────────────────────────────────────────────
        bf = ctk.CTkFrame(scroll, fg_color="transparent")
        bf.grid(row=9, column=0, sticky="e", pady=6)

        ctk.CTkButton(bf, text="Cancel", width=110, height=40, corner_radius=10,
                      font=ctk.CTkFont(size=F["label"]),
                      fg_color="transparent", border_width=1, border_color=T["border"],
                      text_color=T["text_sub"],
                      command=self.destroy).grid(row=0, column=0, padx=8)

        ctk.CTkButton(bf, text="Save", width=130, height=40, corner_radius=10,
                      font=ctk.CTkFont(size=F["label"]),
                      fg_color=T["accent"], hover_color=T["acc_hov"],
                      command=self._save).grid(row=0, column=1, padx=8)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_provider_tab(self, tab, pid: str, models: list, T):
        p = self.cfg.get_provider_config(pid)

        if pid in _PROVIDER_HINTS:
            hint_text, hint_key = _PROVIDER_HINTS[pid]
            ctk.CTkLabel(tab, text=hint_text,
                         font=ctk.CTkFont(size=F["small"]),
                         text_color=T[hint_key],
                         ).grid(row=0, column=0, sticky="w", padx=18, pady=(10, 0))

        r = 2 if pid in _PROVIDER_HINTS else 0

        ctk.CTkLabel(tab, text="API Key",
                     font=ctk.CTkFont(size=F["label"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=r, column=0, sticky="w", padx=18, pady=(14, 4))

        key_entry = ctk.CTkEntry(tab, width=640, show="*",
                                  placeholder_text="Paste your API key here…",
                                  font=ctk.CTkFont(size=F["label"]))
        key_entry.grid(row=r + 1, column=0, sticky="ew", padx=18)
        stored_key = p.get("api_key", "")
        if stored_key and pid != "ollama":
            key_entry.insert(0, stored_key)

        ctk.CTkLabel(tab, text="Model",
                     font=ctk.CTkFont(size=F["label"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=r + 2, column=0, sticky="w", padx=18, pady=(14, 4))

        model_var = ctk.StringVar(value=p.get("model", models[0]))
        ctk.CTkComboBox(tab, values=models, variable=model_var, width=640,
                        font=ctk.CTkFont(size=F["label"]),
                        ).grid(row=r + 3, column=0, sticky="ew", padx=18)

        ctk.CTkLabel(tab, text="Base URL  (optional — custom endpoints / Azure / proxies)",
                     font=ctk.CTkFont(size=F["label"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=r + 4, column=0, sticky="w", padx=18, pady=(14, 4))

        url_entry = ctk.CTkEntry(tab, width=640,
                                  placeholder_text="https://…  (leave blank for default)",
                                  font=ctk.CTkFont(size=F["label"]))
        url_entry.grid(row=r + 5, column=0, sticky="ew", padx=18, pady=(0, 18))
        if p.get("base_url"):
            url_entry.insert(0, p["base_url"])

        self._entries[pid] = {
            "api_key":   key_entry,
            "model_var": model_var,
            "base_url":  url_entry,
        }

    def _setting_combo(self, parent, col: int, label: str, values: list,
                       var: ctk.StringVar, T):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=col, padx=20, pady=20)
        ctk.CTkLabel(f, text=label,
                     font=ctk.CTkFont(size=F["label"], weight="bold"),
                     text_color=T["text"],
                     ).grid(row=0, column=0, pady=(0, 6))
        ctk.CTkComboBox(f, values=values, variable=var, width=160, height=38,
                        font=ctk.CTkFont(size=F["label"]),
                        ).grid(row=1, column=0)

    def _sync_tab(self):
        pid = self._prov_var.get()
        name = _TAB_NAMES.get(pid, "Claude")
        try:
            self._tabs.set(name)
        except Exception:
            pass

    def _save(self):
        cfg = self.cfg
        cfg.set("ai_provider", self._prov_var.get())
        cfg.set("appearance_mode", self._theme_var.get().lower())

        for pid, e in self._entries.items():
            cfg.set_provider_config(pid, "api_key",  e["api_key"].get().strip())
            cfg.set_provider_config(pid, "model",    e["model_var"].get().strip())
            cfg.set_provider_config(pid, "base_url", e["base_url"].get().strip())

        try:
            cfg.set("num_questions", int(self._num_var.get()))
        except ValueError:
            pass

        cfg.set("experience_level", self._exp_var.get())
        cfg.save()

        # Apply theme immediately
        new_mode = self._theme_var.get().lower()
        theme.set_mode(new_mode)
        self.destroy()
