import json
import env
import os
import random
import string
import time
from models.__schema__ import Collection
from models.__users__ import UserData
from datetime import datetime, UTC
from typing import Literal


class ItemData(Collection):
    BASE = "items"
    id: str
    name: str
    price: float
    created_at: datetime
    author_id: int
    description: str
    buyers: list[int] = None
    denied_at: datetime = None
    approved_at: datetime = None
    feedback: str = None
    image: str = None
    status: Literal["pending", "denied", "approved"] = "pending"

    @property
    def author(self) -> UserData | None:
        return UserData.read(self.author_id)

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_denied(self) -> bool:
        return self.status == "denied"

    @property
    def is_approved(self) -> bool:
        return self.status == "approved"

    @classmethod
    def __get_ids(cls) -> list[str]:
        return [
            filename[: filename.index(".")]
            for filename in os.listdir(f"{env.BASE_DIR}/data/{cls.BASE}")
        ]

    @classmethod
    def __get_id(cls) -> list[str]:
        ids = cls.__get_ids()
        _id: str
        while True:
            __id = list(str(int(time.time()))) + random.choices(
                string.ascii_letters, k=8
            )
            random.shuffle(__id)
            _id = "".join(__id)
            if _id not in ids:
                break
        return _id

    @classmethod
    def read(cls, id: str):
        try:
            with open(f"{env.BASE_DIR}/data/{cls.BASE}/{id}.json", "r") as file:
                return cls(id=str(id), **json.load(file))
        except FileNotFoundError:
            return None

    @classmethod
    def create(cls, name: str, price: float, author_id: int, description: str):
        item = cls(
            id=cls.__get_id(),
            name=name,
            price=price,
            author_id=author_id,
            created_at=str(datetime.now(UTC)),
            description=description,
        )

        return item.update()

    def buy(self, buyer: UserData):
        self.buyers = self.buyers or []
        self.buyers.append(int(buyer.id))
        self.author.add_coins(self.price, f"{self.name} purchase")
        buyer.sub_coins(self.price, f"{self.name} purchase")
        return self.update()
