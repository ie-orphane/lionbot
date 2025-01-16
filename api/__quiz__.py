from . import __self__ as api
import random
from env import QUIZ_API_ENDPOINT, QUIZ_API_KEY
from models import QuizData
import asyncio
from constants import COLOR, Quiz


__all__ = ["QuizApi"]


class QuizApi:

    @classmethod
    async def get(cls):
        while True:
            url = f"{QUIZ_API_ENDPOINT}/questions"
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

            if (data is None) or (QuizData.exits(id=data[0]["id"])):
                asyncio.sleep(1.75)
                continue

            return QuizData.create(**data[0], color=color or COLOR.black)
