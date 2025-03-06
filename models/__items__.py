import json
import env
import os
from models.__schema__ import Collection
from models.__users__ import UserData
from uuid import uuid4
from datetime import datetime, UTC
from typing import Literal


class ItemData(Collection):
    BASE = "items"
    id: str
    title: str
    price: float
    created_at: datetime
    author_id: int
    description: str = None
    denied_at: datetime = None
    approved_at: datetime = None
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
    def read(cls, id: str):
        try:
            with open(f"{env.BASE_DIR}/data/{cls.BASE}/{id}.json", "r") as file:
                return cls(id=str(id), **json.load(file))
        except FileNotFoundError:
            return None

    @classmethod
    def create(cls, title: str, price: float, author_id: int, description: str = None):
        ids = cls.__get_ids()

        item_id = None
        while True:
            item_id = str(uuid4())
            if item_id and item_id not in ids:
                break

        item = cls(
            id=item_id,
            title=title,
            price=price,
            author_id=author_id,
            created_at=str(datetime.now(UTC)),
        )
        if description is not None:
            item.description = description

        return item.update()
