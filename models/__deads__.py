import json
from datetime import datetime, UTC
from models.__schema__ import Model, ModelEncoder


class DeadData(Model):
    BASE: str = "data/deads"
    channel: int
    time: datetime

    def __to_dict__(self):
        self.__dict__.update(time=str(self.time))
        return self.__dict__

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__

    @classmethod
    def create(cls, **data):
        deads = DeadData.read_all()
        channels = [dead.channel for dead in deads]
        if data["channel"] in channels:
            raise FileExistsError()
        deads.append(DeadData(**data))
        with open(f"{cls.BASE}.json", "w") as file:
            json.dump(deads, file, cls=ModelEncoder, indent=2)

    @classmethod
    def read_all(cls):
        with open(f"{cls.BASE}.json", "r") as file:
            return [
                cls(channel=x["channel"], time=datetime.fromisoformat(x["time"]))
                for x in json.load(file)
            ]

    def remove(self):
        deads = DeadData.read_all()
        deads.remove(self)
        with open(f"{self.BASE}.json", "w") as file:
            json.dump(deads, file, cls=ModelEncoder, indent=2)
