import os
import json
import env
import datetime as dt
from typing import Literal, Self
from .__schema__ import Collection
import random
from string import ascii_lowercase

class QuizFields:
    id: int
    ID: int
    question: str
    description: str | None
    answers: dict[Literal["a", "b", "c", "d", "e", "f"], str]
    multiple_correct_answers: bool
    correct_answers: dict[Literal["a", "b", "c", "d", "e", "f"], bool]
    explanation: str | None
    tip: str | None
    tags: list[Literal["BASH", "HTML", "Git", "JavaScript", "Python"]]
    category: Literal["bash", "Code", "React", "Laravel"]
    difficulty: Literal["Easy", "Medium", "Hard"]
    message_id: int = 0
    emojis: dict
    contributions: dict[str, str]
    date: dt.date | None = None
    ended: bool = False


class QuizData(Collection, QuizFields):
    BASE = "quizes"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.date:
            self.date = dt.date.fromisoformat(self.date)

    def __to_dict__(self):
        self_dict = super().__to_dict__()
        if (date := self_dict.get("date")):
            self_dict["date"] = str(date)
        return self_dict

    @classmethod
    def create(cls, **kwargs) -> Self:
        del kwargs["correct_answer"]
        new = cls(**kwargs)
        answers = [
           ( answer, new.correct_answers[answerkey+"_correct"] )
            for answerkey, answer in new.answers.items()
            if answer is not None
        ]
        random.shuffle(answers)
        new.answers = {}
        new.correct_answers = {}
        for key, (answer, is_correct) in zip(ascii_lowercase, answers):
            new.answers[key] = answer
            new.correct_answers[key] = is_correct
        new.multiple_correct_answers = json.loads(new.multiple_correct_answers)
        new.tags = [
            tag["name"] for tag in new.tags if tag["name"].lower() != new.category
        ]
        new.ID = new.id
        new.emojis = {}
        new.contributions = {}
        new.id = len(os.listdir(f"{env.BASE_DIR}/data/{cls.BASE}"))
        new.update()
        return new

    @classmethod
    def last(cls) -> Self | None:
        all_quizes = sorted(cls.read_all(), key=lambda x: x.id)
        try:
            return all_quizes[-1]
        except IndexError:
            return None

    @classmethod
    def exits(cls, id: str | int) -> bool:
        return str(id) in [quiz.ID for quiz in cls.read_all()]
