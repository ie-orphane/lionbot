import json
from datetime import datetime
from models.__schema__ import Document


class ChannelData(Document):
    BASE: str = "channels"
    id: int
    role: int
    time: datetime

    def __to_dict__(self):
        self.__dict__.update(time=str(self.time))
        return self.__dict__

    @classmethod
    def read_all(cls):
        with open(f"./data/{cls.BASE}.json", "r") as file:
            return [
                cls(id=x["id"], role=x["role"], time=datetime.fromisoformat(x["time"]))
                for x in json.load(file)
            ]
