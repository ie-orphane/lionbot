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
            case "%d":
                formatted_date = (
                    f"{datetime.fromisoformat(self.moment).strftime('%d %b %Y'):<13}"
                )
                return formatted_date
            case "%m":
                formatted_time = (
                    f"{datetime.fromisoformat(self.moment).strftime('%H:%M:%S'):<10}"
                )
                return formatted_time
            case "%t":
                type_converter = {"deposit": "+", "receive": "+", "send": "-"}
                return type_converter[self.type]


class UserData(Data):
    BASE = "data/users"
    id: int
    name: str
    coins: int
    token: str
    github: str
    portfolio: str
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
