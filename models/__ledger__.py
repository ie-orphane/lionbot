import csv
from models.__schema__ import Model
from typing import Self, List, Literal
import datetime as dt
from zoneinfo import ZoneInfo

__all__ = ["UserLedger"]


class UserLedger(Model):
    BASE = "data/transactions.csv"
    id: int
    datetime: dt.datetime
    amount: float
    reason: str
    current: int
    operation: Literal["add", "sub"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = int(self.id)
        self.datetime = dt.datetime.fromisoformat(self.datetime)

    @classmethod
    def get(cls: Self, user_id: int | str) -> List[Self]:
        ledger = []
        with open(cls.BASE, mode="r", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if None in row:
                    row["reason"] = ",".join([row["reason"]] + row[None])
                    del row[None]

                if row["id"] == str(user_id):
                    ledger.append(cls(**row))

        return ledger

    @property
    def datetimezone(self) -> int:
        return self.datetime.astimezone(ZoneInfo("Africa/Casablanca"))

    @property
    def op(self) -> Literal["\u001b[0;0m", "\u001b[0;32m+", "\u001b[0;31m-"]:
        return {"sub": "\u001b[0;31m-", "add": "\u001b[0;32m+"}.get(
            self.operation, "\u001b[0;0m"
        )
