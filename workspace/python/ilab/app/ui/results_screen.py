from typing import Callable, Optional

import customtkinter as ctk

from .. import theme
from ..theme import F, cat_color
from ..models.question import QuizResult


class ResultsScreen(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        result: QuizResult,
        on_restart: Callable,
        on_home: Callable,
    ):
        T = theme.get()
        super().__init__(parent, fg_color=T["bg_root"])
        self.result = result
        self.on_restart = on_restart
        self.on_home = on_home

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color=T["bg_root"])
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        pct = result.percentage
        if pct >= 80:
            score_color = T["ok_fg"]
        elif pct >= 60:
            score_color = T["amber"]
        else:
            score_color = T["err_fg"]

        grade = (
            "Outstanding!" if pct >= 90 else
            "Excellent!"   if pct >= 80 else
            "Good Job!"    if pct >= 70 else
            "Keep Practising" if pct >= 50 else
            "Needs Improvement"
        )

        # ── Score card ────────────────────────────────────────────────────────
        sc = ctk.CTkFrame(
            scroll, fg_color=T["bg_card"], corner_radius=20,
            border_width=2, border_color=score_color,
        )
        sc.grid(row=0, column=0, padx=28, pady=(22, 14), sticky="ew")
        sc.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            sc, text="Interview Complete",
            font=ctk.CTkFont(size=F["h1"] + 4, weight="bold"),
            text_color=T["text"],
        ).grid(row=0, column=0, columnspan=4, pady=(28, 2))

        ctk.CTkLabel(
            sc, text=grade,
            font=ctk.CTkFont(size=F["h2"], weight="bold"),
            text_color=score_color,
        ).grid(row=1, column=0, columnspan=4, pady=(0, 18))

        skipped = result.timed_out_count
        stat_data = [
            (f"{result.score}/{result.total}", "Score",     score_color),
            (f"{pct:.0f}%",                    "Percentage", score_color),
            (str(result.correct_count),        "Correct",   T["ok_fg"]),
            (str(skipped) if skipped else "—", "Skipped",
             T["err_fg"] if skipped else T["text_mute"]),
        ]

        for col, (val, lbl, clr) in enumerate(stat_data):
            sf = ctk.CTkFrame(sc, fg_color=T["bg_option"], corner_radius=12,
                               border_width=1, border_color=clr)
            sf.grid(row=2, column=col, padx=12, pady=(0, 22), sticky="ew")
            ctk.CTkLabel(
                sf, text=val,
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=clr,
            ).grid(row=0, column=0, padx=24, pady=(16, 2))
            ctk.CTkLabel(
                sf, text=lbl,
                font=ctk.CTkFont(size=F["small"]),
                text_color=T["text_sub"],
            ).grid(row=1, column=0, padx=24, pady=(0, 14))

        bar = ctk.CTkProgressBar(
            sc, height=10, progress_color=score_color,
            fg_color=T["bg_option"], corner_radius=5,
        )
        bar.grid(row=3, column=0, columnspan=4, sticky="ew", padx=28, pady=(0, 26))
        bar.set(pct / 100)

        # ── Action buttons ────────────────────────────────────────────────────
        bf = ctk.CTkFrame(scroll, fg_color="transparent")
        bf.grid(row=1, column=0, pady=14)

        ctk.CTkButton(
            bf, text="New Interview", width=220, height=52, corner_radius=14,
            font=ctk.CTkFont(size=F["ui"], weight="bold"),
            fg_color=T["accent"], hover_color=T["acc_hov"],
            command=self.on_restart,
        ).grid(row=0, column=0, padx=12)

        ctk.CTkButton(
            bf, text="Home", width=160, height=52, corner_radius=14,
            font=ctk.CTkFont(size=F["ui"]),
            fg_color="transparent", border_width=2, border_color=T["accent"],
            hover_color=T["hover"], text_color=T["accent"],
            command=self.on_home,
        ).grid(row=0, column=1, padx=12)

        # ── Question review ───────────────────────────────────────────────────
        ctk.CTkLabel(
            scroll, text="Question Review",
            font=ctk.CTkFont(size=F["h1"], weight="bold"),
            text_color=T["text"],
        ).grid(row=2, column=0, sticky="w", padx=28, pady=(10, 6))

        for i, (q, a) in enumerate(zip(result.questions, result.answers)):
            self._add_review(scroll, row=i + 3, num=i + 1, question=q, answer=a, T=T)

    def _add_review(self, parent, row: int, num: int, question, answer: Optional[int], T):
        skipped = answer is None
        correct = not skipped and question.is_correct(answer)

        if skipped:
            bc, st, sc = T["border"], "SKIPPED", T["text_mute"]
        elif correct:
            bc, st, sc = T["ok_fg"], "CORRECT",  T["ok_fg"]
        else:
            bc, st, sc = T["err_fg"], "INCORRECT", T["err_fg"]

        cat_fg, cat_bg = cat_color(question.category)

        card = ctk.CTkFrame(
            parent, fg_color=T["bg_card"], corner_radius=14,
            border_width=1, border_color=bc,
        )
        card.grid(row=row, column=0, padx=28, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Question row
        qr = ctk.CTkFrame(card, fg_color="transparent")
        qr.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        qr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            qr, text=f"  {question.category}  ",
            font=ctk.CTkFont(size=F["badge"]),
            text_color=cat_fg, fg_color=cat_bg, corner_radius=5,
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        ctk.CTkLabel(
            qr, text=f"Q{num}.  {question.text}",
            font=ctk.CTkFont(size=F["label"]), text_color=T["text"],
            wraplength=720, justify="left", anchor="w",
        ).grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(
            qr, text=f"  {st}  ",
            font=ctk.CTkFont(size=F["badge"], weight="bold"),
            text_color=sc,
            fg_color=T["ok_bg"] if correct else (T["err_bg"] if not skipped else T["bg_option"]),
            corner_radius=6,
        ).grid(row=1, column=1, padx=(10, 0), sticky="e")

        # Options
        af = ctk.CTkFrame(card, fg_color="transparent")
        af.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 6))
        af.grid_columnconfigure(0, weight=1)

        for i, opt in enumerate(question.options):
            is_correct_opt = i == question.correct_index
            is_selected    = i == answer

            if is_correct_opt and is_selected:
                fg_bg, fg_tx = T["ok_bg"], T["ok_fg"]
            elif is_correct_opt:
                fg_bg, fg_tx = T["ok_bg"], T["ok_fg"]
            elif is_selected:
                fg_bg, fg_tx = T["err_bg"], T["err_fg"]
            else:
                fg_bg, fg_tx = "transparent", T["text_mute"]

            mark = "✓" if is_correct_opt else ("✗" if is_selected and not is_correct_opt else " ")
            row_f = ctk.CTkFrame(af, fg_color=fg_bg, corner_radius=7)
            row_f.grid(row=i, column=0, sticky="ew", pady=2)
            af.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row_f,
                text=f"  {mark}  {'ABCD'[i]}.  {opt}",
                font=ctk.CTkFont(size=F["small"]),
                text_color=fg_tx, anchor="w",
            ).grid(row=0, column=0, padx=8, pady=4, sticky="w")

        if question.explanation:
            ctk.CTkLabel(
                card, text=f"💡  {question.explanation}",
                font=ctk.CTkFont(size=F["badge"], slant="italic"),
                text_color=T["text_mute"], wraplength=820, justify="left",
            ).grid(row=2, column=0, sticky="ew", padx=18, pady=(2, 12))
