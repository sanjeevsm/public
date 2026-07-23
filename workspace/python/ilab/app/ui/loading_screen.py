from typing import Callable, List

import customtkinter as ctk

from .. import theme
from ..theme import F
from ..models.question import Question
from ..services.question_generator import QuestionGenerator


class LoadingScreen(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        jd: str,
        experience_level: str,
        num_questions: int,
        on_success: Callable,
        on_error: Callable,
        on_back: Callable,
        mode: str = "jd",
    ):
        T = theme.get()
        super().__init__(parent, fg_color=T["bg_root"])
        self._cancelled = False
        self.on_success = on_success
        self.on_error = on_error
        self.on_back = on_back

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=0, column=0)
        center.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            center, text="iLab+",
            font=ctk.CTkFont(size=F["brand"], weight="bold"),
            text_color=T["accent"],
        ).grid(row=0, column=0, pady=(0, 6))

        subtitle = (
            "Generating questions from your skills…"
            if mode == "skills" else
            "Generating your personalised interview…"
        )
        ctk.CTkLabel(
            center, text=subtitle,
            font=ctk.CTkFont(size=F["h2"]), text_color=T["text_sub"],
        ).grid(row=1, column=0, pady=(0, 28))

        self._progress = ctk.CTkProgressBar(center, width=440, height=8,
                                             progress_color=T["accent"])
        self._progress.grid(row=2, column=0, pady=(0, 14))
        self._progress.configure(mode="indeterminate")
        self._progress.start()

        self._status = ctk.CTkLabel(
            center, text="Connecting to AI provider…",
            font=ctk.CTkFont(size=F["label"]), text_color=T["teal"],
        )
        self._status.grid(row=3, column=0, pady=(0, 6))

        ctk.CTkLabel(
            center,
            text=f"Requesting {num_questions} questions  ·  {experience_level} level",
            font=ctk.CTkFont(size=F["small"]), text_color=T["text_mute"],
        ).grid(row=4, column=0, pady=(0, 26))

        ctk.CTkButton(
            center, text="Cancel",
            width=120, height=38, corner_radius=10,
            font=ctk.CTkFont(size=F["label"]),
            fg_color="transparent", border_width=1, border_color=T["border"],
            hover_color=T["hover"], text_color=T["text_sub"],
            command=self._cancel,
        ).grid(row=5, column=0)

        QuestionGenerator().generate_async(
            jd=jd,
            experience_level=experience_level,
            num_questions=num_questions,
            mode=mode,
            on_success=self._on_success,
            on_error=self._on_error,
            on_progress=self._on_progress,
        )

    def _on_progress(self, msg: str):
        if not self._cancelled:
            self.after(0, lambda: self._status.configure(text=msg))

    def _on_success(self, questions: List[Question]):
        if not self._cancelled:
            self.after(0, lambda: self._do_success(questions))

    def _do_success(self, questions: List[Question]):
        try:
            self.on_success(questions)
        except Exception as e:
            self._show_error(e)

    def _on_error(self, exc: Exception):
        if not self._cancelled:
            self.after(0, lambda: self._show_error(exc))

    def _show_error(self, exc: Exception):
        T = theme.get()
        self._progress.stop()
        self._status.configure(
            text=f"Error: {exc}",
            text_color=T["err_fg"],
            wraplength=440,
        )

    def _cancel(self):
        self._cancelled = True
        self.on_back()
