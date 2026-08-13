import json
import re
from abc import ABC, abstractmethod
from typing import List

from ..models.question import Question


class BaseProvider(ABC):
    @abstractmethod
    def generate_questions(
        self,
        jd: str,
        experience_level: str,
        num_questions: int,
        mode: str = "jd",
    ) -> List[Question]:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def _build_prompt(self, jd: str, experience_level: str, num_questions: int, mode: str = "jd") -> str:
        level_desc = {
            "junior": "0-2 years of experience; focus on fundamentals, syntax, basic patterns",
            "mid": "2-5 years; focus on practical implementation, problem-solving, design patterns",
            "senior": "5+ years; focus on architecture, optimization, trade-offs, system design",
            "lead": "8+ years; focus on technical strategy, system design, scalability, mentoring",
        }.get(experience_level, "2-5 years; focus on practical skills")

        if mode == "skills":
            input_section = f"Target Skills / Technologies:\n---\n{jd}\n---"
            relevance_rule = "Every question must directly test one or more of the listed skills/technologies."
        else:
            input_section = f"Job Description:\n---\n{jd}\n---"
            relevance_rule = "Every question must be directly relevant to the specific technologies and responsibilities in the JD."

        return f"""You are an expert technical interviewer with deep knowledge of current industry standards, \
best practices, and real-world engineering challenges.

Generate exactly {num_questions} multiple-choice interview questions.

Experience Level: {experience_level.title()} ({level_desc})

{input_section}

Rules:
1. {relevance_rule}
2. Difficulty must match the experience level — no trivial trivia for senior roles, no architecture for junior.
3. Each question has exactly 4 answer options; only ONE is correct.
4. Vary topics — cover different aspects of the input (do NOT repeat the same concept).
5. Include practical, real-world scenarios and common pitfalls where appropriate.
6. Reference current best practices (2024-2025 industry standards).
7. The explanation should be concise and educational (1-2 sentences).
8. CRITICAL — option balance: all 4 options MUST be similar in length and detail level. Do NOT make the correct answer longer, more specific, or more descriptive than the wrong ones. Wrong answers must be equally plausible and similarly worded — a reader must not be able to guess the correct answer from length or verbosity alone.

Return ONLY a valid JSON array — no markdown, no code fences, no extra text:
[
  {{
    "text": "Question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Why this is correct and others are wrong",
    "category": "Category name (e.g. React Hooks, SQL Indexing, Docker)",
    "difficulty": "easy|medium|hard"
  }}
]"""

    def _parse_questions(self, response_text: str) -> List[Question]:
        text = response_text.strip()

        # Strip markdown code fences if present
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        # Extract JSON array
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            text = match.group()

        data = json.loads(text)
        questions: List[Question] = []

        for item in data:
            if not isinstance(item, dict):
                continue
            options = item.get("options", [])
            if len(options) != 4:
                continue
            correct_index = int(item.get("correct_index", 0))
            if not (0 <= correct_index <= 3):
                correct_index = 0
            questions.append(
                Question(
                    text=str(item.get("text", "")).strip(),
                    options=[str(o).strip() for o in options],
                    correct_index=correct_index,
                    explanation=str(item.get("explanation", "")).strip(),
                    category=str(item.get("category", "General")).strip(),
                    difficulty=str(item.get("difficulty", "medium")).strip().lower(),
                )
            )

        return questions
