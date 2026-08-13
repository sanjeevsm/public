import threading
from typing import Callable, Dict, List, Optional

from ..models.question import Question
from ..ai.provider_factory import get_provider, get_provider_with_creds


class QuestionGenerator:
    def generate_async(
        self,
        jd: str,
        experience_level: str,
        num_questions: int,
        on_success: Callable[[List[Question]], None],
        on_error: Callable[[Exception], None],
        on_progress: Optional[Callable[[str], None]] = None,
        mode: str = "jd",
        provider_creds: Optional[Dict[str, str]] = None,
    ):
        def run():
            try:
                if on_progress:
                    on_progress("Connecting to AI provider...")

                if provider_creds:
                    provider = get_provider_with_creds(
                        provider_creds["provider"],
                        provider_creds["api_key"],
                        provider_creds.get("model", ""),
                        provider_creds.get("base_url", ""),
                    )
                else:
                    provider = get_provider()

                if on_progress:
                    action = "Analyzing skills and crafting questions..." if mode == "skills" \
                        else "Analyzing job description and crafting questions..."
                    on_progress(action)

                questions = provider.generate_questions(jd, experience_level, num_questions, mode=mode)

                if not questions:
                    raise ValueError(
                        "No questions were generated. "
                        "Please check your API key, model settings, and try again."
                    )

                if on_progress:
                    on_progress(f"Generated {len(questions)} questions successfully!")

                on_success(questions)
            except Exception as exc:
                on_error(exc)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
