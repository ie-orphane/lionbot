from . import __self__ as api
import random
from env import QUIZ_API_URL, QUIZ_API_KEY
from models import QuizData
import asyncio
from consts import COLOR, Quiz
from typing import Any


__all__ = ["QuizApi"]


ATTEMPTES = 5


class QuizApi:

    @classmethod
    async def get(cls) -> Any | None:
        attempts = 0
        while True:
            url = f"{QUIZ_API_URL}/questions"
            if random.choice([True, False]):
                tag = random.choice(Quiz.TAGS)
                color = Quiz.COLORS.get(tag.lower())
                data = await api.get(url, apiKey=QUIZ_API_KEY, tags=tag, limit=1)
            else:
                category = random.choice(Quiz.CATEGORIES)
                color = Quiz.COLORS.get(category.lower())
                data = await api.get(
                    url,
                    apiKey=QUIZ_API_KEY,
                    category=category,
                    limit=1,
                )
            attempts += 1
            if (data is None) and (attempts == ATTEMPTES):
                return None
            if (data is None) or (QuizData.exits(id=data[0]["id"])):
                asyncio.sleep(1.75)
                continue
            if data[0]["category"] == "Linux" or "Ubuntu" in [
                tag["name"] for tag in data[0]["tags"]
            ]:
                continue
            return QuizData.create(**data[0], color=color or COLOR.black)
