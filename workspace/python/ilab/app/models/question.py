from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Question:
    text: str
    options: List[str]
    correct_index: int
    explanation: str = ""
    category: str = ""
    difficulty: str = "medium"

    def is_correct(self, selected_index: int) -> bool:
        return selected_index == self.correct_index

    @property
    def correct_answer(self) -> str:
        if 0 <= self.correct_index < len(self.options):
            return self.options[self.correct_index]
        return ""


@dataclass
class QuizResult:
    questions: List[Question] = field(default_factory=list)
    answers: List[Optional[int]] = field(default_factory=list)
    time_taken: List[float] = field(default_factory=list)

    @property
    def score(self) -> int:
        return sum(
            1 for q, a in zip(self.questions, self.answers)
            if a is not None and q.is_correct(a)
        )

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def percentage(self) -> float:
        return (self.score / self.total * 100) if self.total else 0.0

    @property
    def timed_out_count(self) -> int:
        return sum(1 for a in self.answers if a is None)

    @property
    def correct_count(self) -> int:
        return self.score

    @property
    def incorrect_count(self) -> int:
        return sum(
            1 for q, a in zip(self.questions, self.answers)
            if a is not None and not q.is_correct(a)
        )
