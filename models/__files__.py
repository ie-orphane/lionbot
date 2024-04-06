import json, os
from datetime import datetime
from models.__schema__ import Model, ModelEncoder


class FileData(Model):
    BASE: str = "data/files"
    channel: int
    name: str
    time: datetime

    def __to_dict__(self):
        self.__dict__.update(time=str(self.time))
        return self.__dict__

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__

    @classmethod
    def exists(cls, name: int) -> bool:
        return name in os.listdir("assets/files")

    @classmethod
    def create(cls, **data) -> None:
        files = FileData.read_all()
        files.append(FileData(**data))
        with open(f"{cls.BASE}.json", "w") as file:
            json.dump(files, file, cls=ModelEncoder, indent=2)

    @classmethod
    def read_all(cls):
        with open(f"{cls.BASE}.json", "r") as file:
            return [
                cls(
                    channel=x["channel"],
                    time=datetime.fromisoformat(x["time"]),
                    name=x["name"],
                )
                for x in json.load(file)
            ]

    def remove(self) -> None:
        files = FileData.read_all()
        files.remove(self)
        os.remove(f"assets/files/{self.name}")
        with open(f"{self.BASE}.json", "w") as file:
            json.dump(files, file, cls=ModelEncoder, indent=2)
