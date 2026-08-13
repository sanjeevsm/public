from typing import Callable

import customtkinter as ctk

from .. import theme
from ..theme import F
from ..config import get_config


class JDScreen(ctk.CTkFrame):
    def __init__(self, parent, on_generate: Callable, on_back: Callable):
        T = theme.get()
        super().__init__(parent, fg_color=T["bg_root"])
        self.on_generate = on_generate
        self.on_back = on_back
        self.cfg = get_config()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=T["bg_header"], corner_radius=0, height=62)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_propagate(False)

        ctk.CTkButton(
            hdr, text="← Back", width=85, height=36,
            font=ctk.CTkFont(size=F["label"]),
            fg_color="transparent", hover_color=T["hover"],
            text_color=T["text_sub"],
            command=self.on_back,
        ).grid(row=0, column=0, padx=14, pady=13)

        ctk.CTkLabel(
            hdr, text="Interview Setup",
            font=ctk.CTkFont(size=F["h1"], weight="bold"),
            text_color=T["accent"],
        ).grid(row=0, column=1, pady=13)

        # ── Scrollable body ───────────────────────────────────────────────────
        body = ctk.CTkScrollableFrame(self, fg_color=T["bg_root"])
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=12)
        body.grid_columnconfigure(0, weight=1)

        # ── Input tabs ────────────────────────────────────────────────────────
        tab_kwargs = dict(
            height=280,
            fg_color=T["bg_card"],
            segmented_button_fg_color=T["bg_header"],
            segmented_button_selected_color=T["border"],
            segmented_button_selected_hover_color=T["border_md"],
            segmented_button_unselected_color=T["bg_header"],
            segmented_button_unselected_hover_color=T["hover"],
        )
        self._tabs = ctk.CTkTabview(body, **tab_kwargs)
        self._tabs.grid(row=0, column=0, sticky="ew", pady=(4, 0))

        self._tabs.add("Job Description")
        self._tabs.add("Skills")

        self._build_jd_tab(self._tabs.tab("Job Description"), T)
        self._build_skills_tab(self._tabs.tab("Skills"), T)

        # ── Settings row ──────────────────────────────────────────────────────
        sf = ctk.CTkFrame(body, fg_color=T["bg_card"], corner_radius=14,
                           border_width=1, border_color=T["border"])
        sf.grid(row=1, column=0, sticky="ew", pady=(14, 18))
        sf.grid_columnconfigure((0, 1), weight=1)

        self._exp_var = ctk.StringVar(value=self.cfg.experience_level)
        self._num_var = ctk.StringVar(value=str(self.cfg.num_questions))

        self._add_combo(sf, col=0, label="Experience Level",
                        values=["junior", "mid", "senior", "lead", "architect"],
                        var=self._exp_var, T=T)
        self._add_combo(sf, col=1, label="No. of Questions",
                        values=["5", "10", "15", "20", "25", "30"],
                        var=self._num_var, T=T)

        # ── Generate button ───────────────────────────────────────────────────
        ctk.CTkButton(
            body,
            text="  Generate Interview Questions  ",
            font=ctk.CTkFont(size=F["ui"], weight="bold"),
            height=54, corner_radius=14,
            fg_color=T["accent"], hover_color=T["acc_hov"],
            command=self._on_generate,
        ).grid(row=2, column=0, sticky="ew", pady=(0, 20))

    # ── Tab builders ──────────────────────────────────────────────────────────

    def _build_jd_tab(self, tab, T):
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tab,
            text="Paste or type any job description — a full JD, a title, or a single role keyword.",
            font=ctk.CTkFont(size=F["small"]), text_color=T["text_sub"],
            wraplength=780, justify="left",
        ).grid(row=0, column=0, sticky="w", padx=6, pady=(8, 6))

        self.jd_box = ctk.CTkTextbox(
            tab, height=200, font=ctk.CTkFont(size=F["label"]),
            border_width=1, border_color=T["border"],
            fg_color=T["bg_input"], text_color=T["text"],
        )
        self.jd_box.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))
        _ph = "e.g.  Senior Python Developer with FastAPI, PostgreSQL and AWS experience…"
        self.jd_box.insert("1.0", _ph)
        self.jd_box.bind("<FocusIn>",
                         lambda e: self._clear_ph(self.jd_box, "e.g.  Senior"))

    def _build_skills_tab(self, tab, T):
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tab,
            text="List the skills or technologies to focus on — separate with commas, newlines, or spaces.",
            font=ctk.CTkFont(size=F["small"]), text_color=T["text_sub"],
            wraplength=780, justify="left",
        ).grid(row=0, column=0, sticky="w", padx=6, pady=(8, 6))

        self.skills_box = ctk.CTkTextbox(
            tab, height=200, font=ctk.CTkFont(size=F["label"]),
            border_width=1, border_color=T["border"],
            fg_color=T["bg_input"], text_color=T["text"],
        )
        self.skills_box.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))
        _ph = "e.g.  React, TypeScript, Node.js, PostgreSQL, Docker, AWS Lambda, CI/CD"
        self.skills_box.insert("1.0", _ph)
        self.skills_box.bind("<FocusIn>",
                             lambda e: self._clear_ph(self.skills_box, "e.g.  React"))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _clear_ph(self, box: ctk.CTkTextbox, prefix: str):
        if box.get("1.0", "end").strip().startswith(prefix):
            box.delete("1.0", "end")

    def _add_combo(self, parent, col: int, label: str, values: list,
                   var: ctk.StringVar, T: dict):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=col, padx=22, pady=20)
        ctk.CTkLabel(f, text=label,
                     font=ctk.CTkFont(size=F["label"], weight="bold"),
                     text_color=T["text"]).grid(row=0, column=0, pady=(0, 6))
        ctk.CTkComboBox(f, values=values, variable=var, width=165, height=38,
                        font=ctk.CTkFont(size=F["label"]),
                        text_color=T["text"]).grid(row=1, column=0)

    def _on_generate(self):
        active_tab = self._tabs.get()

        if active_tab == "Job Description":
            text = self.jd_box.get("1.0", "end").strip()
            is_placeholder = text.startswith("e.g.  Senior")
            mode = "jd"
        else:
            text = self.skills_box.get("1.0", "end").strip()
            is_placeholder = text.startswith("e.g.  React")
            mode = "skills"

        if not text or is_placeholder:
            import tkinter.messagebox as mb
            field = "job description" if mode == "jd" else "skills"
            mb.showwarning("Missing Input", f"Please enter a {field} before generating.")
            return

        exp = self._exp_var.get()
        try:
            num = int(self._num_var.get())
        except ValueError:
            num = 10

        cfg = get_config()
        cfg.set("experience_level", exp)
        cfg.set("num_questions", num)
        cfg.save()

        self.on_generate(text, exp, num, mode)
