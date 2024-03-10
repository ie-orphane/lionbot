import json
from datetime import date
from models.__schema__ import Model, Data


class GeekData(Model):
    id: int
    amount: int
    languages: dict[str, int]


class WeekData(Data):
    BASE = "data/weeks"
    id: int
    start: str
    end: str
    geeks: list[GeekData]

    @classmethod
    def read(cls, id: int | str):
        with open(f"{cls.BASE}/{id}.json", "r") as file:
            data: dict = json.load(file)
            data["geeks"] = [GeekData(**x) for x in data["geeks"]]
            return cls(id=int(id), **data)

    def __format__(self, __format_spec: str) -> str:
        match __format_spec:
            case "%l":
                start = date.fromisoformat(self.start).strftime("%d %b %Y")
                end = date.fromisoformat(self.end).strftime("%d %b %Y")
                formated_date = f"{start} - {end}"
                for repeated_str in set(start.split()) & set(end.split()):
                    formated_date = formated_date.replace(repeated_str, "", 1)
                return formated_date
