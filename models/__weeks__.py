from datetime import date
from models.__schema__ import Data


class WeekData(Data):
    BASE = "weeks"
    id: int
    start: str
    end: str
    geeks: dict

    def __format__(self, __format_spec: str) -> str:
        match __format_spec:
            case "%l":
                start = date.fromisoformat(self.start).strftime("%d %b %Y")
                end = date.fromisoformat(self.end).strftime("%d %b %Y")
                formated_date = f"{start} - {end}"
                for repeated_str in set(start.split()) & set(end.split()):
                    formated_date = formated_date.replace(repeated_str, "", 1)
                return formated_date
