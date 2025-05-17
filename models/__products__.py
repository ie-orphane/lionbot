import json
import os
import random
import string
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import discord

import env
from consts import SHOP_FEE
from models.__schema__ import Collection
from models.__users__ import UserData


class ProductImage:
    def __init__(self, _id: str, filename: str) -> None:
        if filename is None:
            self.filename = None
            self.path = None
            self.url = None
            return
        self.filename = filename
        self.path = Path(env.BASE_DIR) / "storage" / "images" / f"{_id}_{filename}"
        self.url = f"attachment://{filename}"

    @property
    def file(self) -> discord.File | Any:
        return (
            discord.utils.MISSING
            if self.path is None
            else discord.File(self.path, filename=self.filename)
        )


class ProductSource:
    def __init__(self, _id: str, filename: str) -> None:
        if filename is None:
            self.filename = None
            self.path = None
            return
        self.filename = filename
        self.path = Path(env.BASE_DIR) / "storage" / "files" / f"{_id}_{filename}"

    @property
    def file(self) -> discord.File | Any:
        return (
            discord.utils.MISSING
            if self.path is None
            else discord.File(self.path, filename=self.filename)
        )


class ProductData(Collection):
    BASE = "products"
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
    _image: str = None
    _source: str = None
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
    def image(self) -> ProductImage:
        return ProductImage(self.id, self._image)

    @property
    def source(self) -> ProductSource:
        return ProductSource(self.id, self._source)

    @property
    def is_approved(self) -> bool:
        return self.status == "approved"

    @property
    def fee(self) -> float:
        return self.price * SHOP_FEE

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
    def create(
        cls,
        name: str,
        price: float,
        author_id: int,
        description: str,
        image: str | None = None,
        source: str | None = None,
    ):
        product = cls(
            id=cls.__get_id(),
            name=name,
            price=price,
            author_id=author_id,
            created_at=str(datetime.now(UTC)),
            description=description,
        )
        if image is not None:
            product._image = image
        if source is not None:
            product._source = source
        return product.update()

    def buy(self, buyer: UserData):
        self.buyers = self.buyers or []
        self.buyers.append(int(buyer.id))
        self.author.add_coins(self.price, f"{self.name} purchase")
        self.author.sub_coins(self.fee, f"{self.name} purchase fee")
        buyer.sub_coins(self.price, f"{self.name} purchase")
        return self.update()
