import tkinter.messagebox as mb
from typing import Callable, Dict, List, Optional, Set

import customtkinter as ctk

from .. import theme
from ..theme import F, cat_color
from ..models.question import Question, QuizResult


class QuizScreen(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        questions: List[Question],
        on_complete: Callable[[QuizResult], None],
        on_quit: Callable,
    ):
        T = theme.get()
        super().__init__(parent, fg_color=T["bg_root"])
        self._T = T
        self.questions = questions
        self.on_complete = on_complete
        self.on_quit = on_quit

        self._idx = 0
        self._answers: Dict[int, Optional[int]] = {}
        self._bookmarks: Set[int] = set()
        self._bookmark_filter = False
        self._nav_indices: List[int] = list(range(len(questions)))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header(T)
        self._build_body(T)
        self._build_footer(T)
        self._load_question()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, T):
        hdr = ctk.CTkFrame(self, fg_color=T["bg_header"], corner_radius=0, height=62)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_propagate(False)

        ctk.CTkLabel(
            hdr, text="iLab+",
            font=ctk.CTkFont(size=F["h1"], weight="bold"),
            text_color=T["accent"],
        ).grid(row=0, column=0, padx=20)

        self._prog_lbl = ctk.CTkLabel(
            hdr, text="",
            font=ctk.CTkFont(size=F["label"]), text_color=T["text_sub"],
        )
        self._prog_lbl.grid(row=0, column=1)

        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.grid(row=0, column=2, padx=12)

        self._bm_filter_btn = ctk.CTkButton(
            right, text="★  Bookmarks", width=138, height=34, corner_radius=10,
            font=ctk.CTkFont(size=F["label"]),
            fg_color="transparent", border_width=1, border_color=T["bm_off"],
            text_color=T["bm_off"],
            command=self._toggle_bookmark_filter,
        )
        self._bm_filter_btn.grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            right, text="Finish  ✓", width=90, height=34, corner_radius=10,
            font=ctk.CTkFont(size=F["label"]),
            fg_color=T["ok_bg"], border_width=1, border_color=T["ok_fg"],
            hover_color=T["ok_bg"], text_color=T["ok_fg"],
            command=self._finish,
        ).grid(row=0, column=1, padx=(0, 8))

        ctk.CTkButton(
            right, text="Quit", width=64, height=34, corner_radius=10,
            font=ctk.CTkFont(size=F["label"]),
            fg_color="transparent", border_width=1, border_color=T["err_bg"],
            hover_color=T["err_bg"], text_color=T["err_fg"],
            command=self._quit,
        ).grid(row=0, column=2)

    # ── Body ──────────────────────────────────────────────────────────────────

    def _build_body(self, T):
        body = ctk.CTkScrollableFrame(self, fg_color=T["bg_root"])
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(14, 0))
        body.grid_columnconfigure(0, weight=1)
        self._body = body

        # Question card
        qcard = ctk.CTkFrame(
            body, fg_color=T["bg_card"], corner_radius=16,
            border_width=1, border_color=T["border"],
        )
        qcard.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        qcard.grid_columnconfigure(0, weight=1)

        # Meta row
        meta = ctk.CTkFrame(qcard, fg_color="transparent")
        meta.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 4))
        meta.grid_columnconfigure(2, weight=1)

        self._cat_lbl = ctk.CTkLabel(
            meta, text="", font=ctk.CTkFont(size=F["badge"]),
            text_color=T["teal"], fg_color=T["cats"][0][1], corner_radius=6,
        )
        self._cat_lbl.grid(row=0, column=0, sticky="w")

        self._diff_lbl = ctk.CTkLabel(
            meta, text="", font=ctk.CTkFont(size=F["badge"]),
            text_color=T["amber"], fg_color=T["bg_option"], corner_radius=6,
        )
        self._diff_lbl.grid(row=0, column=1, padx=(8, 0), sticky="w")

        self._qnum_lbl = ctk.CTkLabel(
            meta, text="", font=ctk.CTkFont(size=F["small"]),
            text_color=T["text_mute"],
        )
        self._qnum_lbl.grid(row=0, column=2, sticky="e", padx=(0, 8))

        self._bm_btn = ctk.CTkButton(
            meta, text="☆", width=36, height=28, corner_radius=8,
            font=ctk.CTkFont(size=F["ui"]),
            fg_color="transparent", hover_color=T["hover"],
            text_color=T["bm_off"], border_width=1, border_color=T["bm_off"],
            command=self._toggle_bookmark,
        )
        self._bm_btn.grid(row=0, column=3)

        self._q_lbl = ctk.CTkLabel(
            qcard, text="",
            font=ctk.CTkFont(size=F["body"]),
            wraplength=860, justify="left", anchor="w",
            text_color=T["text"],
        )
        self._q_lbl.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))

        # Options
        self._opt_widgets: List[dict] = []
        for i in range(4):
            w = self._make_option(body, i, T)
            w["outer"].grid(row=i + 1, column=0, sticky="ew", pady=4)

        # Explanation panel
        self._exp_frame = ctk.CTkFrame(
            body, fg_color=T["bg_card"], corner_radius=12,
            border_width=1, border_color=T["border"],
        )
        self._exp_lbl = ctk.CTkLabel(
            self._exp_frame, text="",
            font=ctk.CTkFont(size=F["label"], slant="italic"),
            text_color=T["text_sub"], wraplength=860, justify="left",
        )
        self._exp_lbl.grid(row=0, column=0, padx=18, pady=14, sticky="ew")
        self._exp_frame.grid_columnconfigure(0, weight=1)

    def _make_option(self, parent, idx: int, T) -> dict:
        letter = "ABCD"[idx]
        lc, lb = T["opt_letters"][idx]

        outer = ctk.CTkFrame(
            parent, fg_color=T["bg_option"], corner_radius=12,
            border_width=1, border_color=T["border"],
        )
        outer.grid_columnconfigure(1, weight=1)

        badge = ctk.CTkLabel(
            outer, text=letter, width=42, height=42,
            font=ctk.CTkFont(size=F["ui"], weight="bold"),
            text_color=lc, fg_color=lb, corner_radius=10,
        )
        badge.grid(row=0, column=0, padx=(14, 10), pady=14)

        text_lbl = ctk.CTkLabel(
            outer, text="",
            font=ctk.CTkFont(size=F["ui"]), text_color=T["text"],
            wraplength=760, justify="left", anchor="w",
        )
        text_lbl.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=14)

        widgets = {"outer": outer, "badge": badge, "text": text_lbl,
                   "def_lc": lc, "def_lb": lb}
        for w in (outer, badge, text_lbl):
            w.bind("<Button-1>", lambda e, i=idx: self._pick(i))
            w.bind("<Enter>",    lambda e, o=outer: self._hover(o, True))
            w.bind("<Leave>",    lambda e, o=outer: self._hover(o, False))
            w.configure(cursor="hand2")

        self._opt_widgets.append(widgets)
        return widgets

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self, T):
        foot = ctk.CTkFrame(self, fg_color=T["bg_header"], corner_radius=0, height=64)
        foot.grid(row=2, column=0, sticky="ew")
        foot.grid_columnconfigure(1, weight=1)
        foot.grid_propagate(False)

        self._prev_btn = ctk.CTkButton(
            foot, text="← Back", width=120, height=40, corner_radius=10,
            font=ctk.CTkFont(size=F["label"]),
            fg_color="transparent", border_width=1, border_color=T["border"],
            hover_color=T["hover"], text_color=T["text_sub"],
            command=self._prev,
        )
        self._prev_btn.grid(row=0, column=0, padx=(20, 8), pady=12)

        nav_scroll = ctk.CTkScrollableFrame(
            foot, fg_color=T["bg_header"], height=46, orientation="horizontal",
        )
        nav_scroll.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
        self._nav_frame = nav_scroll
        self._dot_btns: List[ctk.CTkButton] = []

        self._next_btn = ctk.CTkButton(
            foot, text="Next →", width=120, height=40, corner_radius=10,
            font=ctk.CTkFont(size=F["label"], weight="bold"),
            fg_color=T["accent"], hover_color=T["acc_hov"],
            command=self._next,
        )
        self._next_btn.grid(row=0, column=2, padx=(8, 20), pady=12)

    # ── Load question ─────────────────────────────────────────────────────────

    def _load_question(self):
        T = self._T
        q = self.questions[self._idx]
        total = len(self.questions)
        nav = self._nav_indices

        prefix = "★  " if self._bookmark_filter else ""
        self._prog_lbl.configure(
            text=f"{prefix}Question  {self._idx + 1}  of  {total}",
        )
        self._qnum_lbl.configure(text=f"# {self._idx + 1}")

        # Category badge
        cat_fg, cat_bg = cat_color(q.category)
        self._cat_lbl.configure(
            text=f"  {q.category}  ", text_color=cat_fg, fg_color=cat_bg,
        )

        # Difficulty badge
        diff_map = {
            "easy":   (T["teal"],  T["bg_option"]),
            "medium": (T["amber"], T["bg_option"]),
            "hard":   (T["coral"], T["bg_option"]),
        }
        df, db = diff_map.get(q.difficulty, (T["text_sub"], T["bg_option"]))
        self._diff_lbl.configure(
            text=f"  {q.difficulty.title()}  ", text_color=df, fg_color=db,
        )

        # Bookmark button
        bm = self._idx in self._bookmarks
        self._bm_btn.configure(
            text="★" if bm else "☆",
            text_color=T["bm_on"] if bm else T["bm_off"],
            border_color=T["bm_on"] if bm else T["bm_off"],
        )

        self._q_lbl.configure(text=q.text)

        # Reset option colors
        for i, w in enumerate(self._opt_widgets):
            w["outer"].configure(fg_color=T["bg_option"], border_color=T["border"])
            w["badge"].configure(text_color=w["def_lc"], fg_color=w["def_lb"])
            w["text"].configure(text=q.options[i], text_color=T["text"])

        answered = self._answers.get(self._idx)
        if answered is not None:
            correct = q.is_correct(answered)
            if correct:
                self._paint(answered, T["ok_bg"], T["ok_fg"])
            else:
                self._paint(answered, T["err_bg"], T["err_fg"])
                self._paint(q.correct_index, T["ok_bg"], T["ok_fg"])
            self._unbind_all()
            self._show_explanation(q, correct=correct)
        else:
            self._rebind_all()
            self._exp_frame.grid_remove()

        self._refresh_nav_dots()
        self._update_nav_buttons()

    # ── Nav dots ──────────────────────────────────────────────────────────────

    def _refresh_nav_dots(self):
        T = self._T
        for b in self._dot_btns:
            b.destroy()
        self._dot_btns.clear()

        for pos, qi in enumerate(self._nav_indices):
            ans = self._answers.get(qi)
            bm = qi in self._bookmarks
            is_cur = qi == self._idx

            if is_cur:
                fg, bg, bc = T["accent"], T["bg_card"], T["accent"]
            elif ans is not None:
                correct = self.questions[qi].is_correct(ans)
                fg = T["ok_fg"] if correct else T["err_fg"]
                bg = T["ok_bg"] if correct else T["err_bg"]
                bc = fg
            else:
                fg, bg, bc = T["text_sub"], T["bg_card"], T["border"]

            label = f"★{qi+1}" if bm else str(qi + 1)
            btn = ctk.CTkButton(
                self._nav_frame, text=label,
                width=36, height=32, corner_radius=8,
                font=ctk.CTkFont(size=F["badge"], weight="bold"),
                fg_color=bg, border_width=1, border_color=bc, text_color=fg,
                command=lambda i=qi: self._jump_to(i),
            )
            btn.grid(row=0, column=pos, padx=3, pady=6)
            self._dot_btns.append(btn)

    def _update_nav_buttons(self):
        T = self._T
        nav = self._nav_indices
        if not nav or self._idx not in nav:
            self._prev_btn.configure(state="disabled")
            self._next_btn.configure(state="disabled")
            return
        pos = nav.index(self._idx)
        self._prev_btn.configure(state="normal" if pos > 0 else "disabled")
        is_last = pos == len(nav) - 1
        self._next_btn.configure(
            text="Finish  ✓" if is_last else "Next →",
            fg_color=T["ok_bg"] if is_last else T["accent"],
            hover_color=T["ok_bg"] if is_last else T["acc_hov"],
            text_color=T["ok_fg"] if is_last else "white",
            border_width=1 if is_last else 0,
            border_color=T["ok_fg"] if is_last else T["acc_hov"],
        )

    # ── Answer selection ──────────────────────────────────────────────────────

    def _pick(self, idx: int):
        T = self._T
        if self._idx in self._answers:
            return
        q = self.questions[self._idx]
        correct = q.is_correct(idx)
        self._answers[self._idx] = idx
        if correct:
            self._paint(idx, T["ok_bg"], T["ok_fg"])
        else:
            self._paint(idx, T["err_bg"], T["err_fg"])
            self._paint(q.correct_index, T["ok_bg"], T["ok_fg"])
        self._show_explanation(q, correct=correct)
        self._unbind_all()
        self._refresh_nav_dots()
        self._update_nav_buttons()

    # ── Bookmark ──────────────────────────────────────────────────────────────

    def _toggle_bookmark(self):
        if self._idx in self._bookmarks:
            self._bookmarks.discard(self._idx)
        else:
            self._bookmarks.add(self._idx)
        self._refresh_bm_filter_btn()
        self._load_question()

    def _refresh_bm_filter_btn(self):
        T = self._T
        count = len(self._bookmarks)
        active = self._bookmark_filter
        label = f"★  Bookmarks ({count})" if count else "★  Bookmarks"
        on = count or active
        self._bm_filter_btn.configure(
            text=label,
            fg_color=T["hover"] if on else "transparent",
            border_color=T["bm_on"] if on else T["bm_off"],
            text_color=T["bm_on"] if on else T["bm_off"],
        )

    def _toggle_bookmark_filter(self):
        if not self._bookmarks:
            return
        self._bookmark_filter = not self._bookmark_filter
        if self._bookmark_filter:
            self._nav_indices = sorted(self._bookmarks)
            if self._idx not in self._nav_indices:
                self._idx = self._nav_indices[0]
        else:
            self._nav_indices = list(range(len(self.questions)))
        self._refresh_bm_filter_btn()
        self._load_question()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _prev(self):
        nav = self._nav_indices
        pos = nav.index(self._idx)
        if pos > 0:
            self._idx = nav[pos - 1]
            self._load_question()

    def _next(self):
        nav = self._nav_indices
        pos = nav.index(self._idx)
        if pos < len(nav) - 1:
            self._idx = nav[pos + 1]
            self._load_question()
        else:
            self._finish()

    def _jump_to(self, qi: int):
        self._idx = qi
        self._load_question()

    # ── Finish / Quit ─────────────────────────────────────────────────────────

    def _finish(self):
        total = len(self.questions)
        unanswered = total - len(self._answers)
        if unanswered and not mb.askyesno(
            "Finish Interview",
            f"You have {unanswered} unanswered question(s).\nFinish anyway?",
            parent=self,
        ):
            return
        result = QuizResult(
            questions=self.questions,
            answers=[self._answers.get(i) for i in range(total)],
            time_taken=[0.0] * total,
        )
        self.on_complete(result)

    def _quit(self):
        if mb.askyesno("Quit Interview", "Quit now? Your progress will be lost.", parent=self):
            self.on_quit()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _paint(self, idx: int, bg: str, fg: str):
        T = self._T
        w = self._opt_widgets[idx]
        w["outer"].configure(fg_color=bg, border_color=fg)
        w["badge"].configure(text_color=fg, fg_color=bg)
        w["text"].configure(text_color=fg)

    def _show_explanation(self, q: Question, correct: bool):
        T = self._T
        if not q.explanation:
            return
        prefix = "✓  Correct!    " if correct else "✗  Incorrect.    "
        color = T["ok_fg"] if correct else T["err_fg"]
        self._exp_lbl.configure(text=prefix + q.explanation, text_color=color)
        self._exp_frame.grid(row=5, column=0, sticky="ew", pady=(6, 4))

    def _hover(self, outer: ctk.CTkFrame, entering: bool):
        T = self._T
        if self._idx not in self._answers:
            outer.configure(fg_color=T["hover"] if entering else T["bg_option"])

    def _rebind_all(self):
        for i, w in enumerate(self._opt_widgets):
            for widget in (w["outer"], w["badge"], w["text"]):
                widget.bind("<Button-1>", lambda e, ii=i: self._pick(ii))
                widget.bind("<Enter>",    lambda e, o=w["outer"]: self._hover(o, True))
                widget.bind("<Leave>",    lambda e, o=w["outer"]: self._hover(o, False))
                widget.configure(cursor="hand2")

    def _unbind_all(self):
        for w in self._opt_widgets:
            for widget in (w["outer"], w["badge"], w["text"]):
                widget.unbind("<Button-1>")
                widget.unbind("<Enter>")
                widget.unbind("<Leave>")
                widget.configure(cursor="")

    def destroy(self):
        super().destroy()
