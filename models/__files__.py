import json, os, env
from datetime import datetime
from models.__schema__ import Document, ModelEncoder


class FileData(Document):
    BASE: str = "files"
    id: str
    channel: int
    time: datetime

    def __to_dict__(self):
        self.__dict__.update(time=str(self.time))
        return self.__dict__

    @classmethod
    def read_all(cls):
        with open(f"{env.BASE_DIR}/data/{cls.BASE}.json") as file:
            return [
                cls(
                    id=x["id"],
                    channel=x["channel"],
                    time=datetime.fromisoformat(x["time"]),
                )
                for x in json.load(file)
            ]

    def remove(self) -> None:
        files = FileData.read_all()
        files.remove(self)
        os.remove(f"{env.BASE_DIR}/storage/files/{self.id}")
        with open(f"{env.BASE_DIR}/data/{self.BASE}.json", "w") as file:
            json.dump(files, file, cls=ModelEncoder, indent=2)
