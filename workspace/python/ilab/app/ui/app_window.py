import tkinter.messagebox as mb
from typing import List, Optional

import customtkinter as ctk

from ..models.question import Question, QuizResult


class AppWindow:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self._current: Optional[ctk.CTkFrame] = None
        self._show_home()

    # ── navigation ────────────────────────────────────────────────────────────

    def _swap(self, new_screen: ctk.CTkFrame):
        if self._current:
            self._current.destroy()
        self._current = new_screen
        new_screen.grid(row=0, column=0, sticky="nsew")

    def _show_home(self):
        from .home_screen import HomeScreen
        self._swap(HomeScreen(self.container, on_start=self._show_jd, on_save=self._show_home))

    def _show_jd(self):
        from .jd_screen import JDScreen
        self._swap(JDScreen(self.container, on_generate=self._start_generation, on_back=self._show_home))

    def _start_generation(self, jd: str, experience_level: str, num_questions: int, mode: str = "jd"):
        from .loading_screen import LoadingScreen
        self._swap(
            LoadingScreen(
                self.container,
                jd=jd,
                experience_level=experience_level,
                num_questions=num_questions,
                mode=mode,
                on_success=self._start_quiz,
                on_error=self._on_gen_error,
                on_back=self._show_jd,
            )
        )

    def _start_quiz(self, questions: List[Question]):
        from .quiz_screen import QuizScreen
        self._swap(
            QuizScreen(
                self.container,
                questions=questions,
                on_complete=self._show_results,
                on_quit=self._show_home,
            )
        )

    def _show_results(self, result: QuizResult):
        from .results_screen import ResultsScreen
        self._swap(
            ResultsScreen(
                self.container,
                result=result,
                on_restart=self._show_jd,
                on_home=self._show_home,
            )
        )

    def _on_gen_error(self, error: Exception):
        self._show_jd()
        msg = str(error)
        low = msg.lower()
        if "credit" in low or "license" in low or "billing" in low or "payment" in low or "quota" in low:
            hint = (
                "Your API account has no credits or active subscription.\n\n"
                "For xAI Grok free tier:\n"
                "  1. Go to console.x.ai\n"
                "  2. Sign in and open Billing\n"
                "  3. Free credits are issued on account creation — check your balance\n"
                "  4. Add a payment method to unlock paid usage"
            )
        elif "connection" in low or "connect" in low:
            hint = (
                "Cannot reach the API server.\n"
                "Check: internet connection, firewall/proxy, and that the Base URL is correct."
            )
        elif "401" in msg or "unauthorized" in low or "invalid" in low and "key" in low:
            hint = "Invalid or missing API key — check your key in Settings."
        elif "model" in low and ("not found" in low or "does not exist" in low):
            hint = "Model not found — check the model name in Settings matches one offered by your provider."
        else:
            hint = "Please check your AI provider settings and try again."
        mb.showerror("Generation Failed", f"{msg}\n\n{hint}", parent=self.root)

