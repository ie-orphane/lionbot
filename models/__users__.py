import json
from datetime import datetime
from typing import Literal
from models.__schema__ import Model, Data


class LedgerData(Model):
    moment: str
    type: Literal["deposit"]
    amount: int

    def __format__(self, __format_spec: str) -> str:
        match __format_spec:
            case "%m":
                formatted_datetime = datetime.fromisoformat(self.moment).strftime(
                    "%Y/%m/%d %H:%M:%S"
                )
                return formatted_datetime
            case "%t":
                type_converter = {"deposit": "+"}
                return type_converter[self.type]


class UserData(Data):
    BASE = "data/users"
    id: int
    name: str
    coins: int
    token: str
    github: str
    ledger: list[LedgerData]

    @classmethod
    def read(cls, id: int | str):
        try:
            with open(f"{cls.BASE}/{id}.json", "r") as file:
                data: dict = json.load(file)
                data["ledger"] = [LedgerData(**x) for x in data["ledger"]]
                return cls(id=int(id), **data)
        except FileNotFoundError:
            return None
