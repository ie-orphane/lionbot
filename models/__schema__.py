import json, os


class Model:
    def __init__(self, **kwargs) -> None:
        self.__dict__ = kwargs

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.__dict__}"

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__

    def __to_dict__(self):
        return self.__dict__


class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.__to_dict__()
        return json.JSONEncoder.default(self, obj)


class Document(Model):
    @classmethod
    def exists(cls, id: str) -> bool:
        docs = [data.id for data in cls.read_all()]
        return id in docs

    @classmethod
    def create(cls, **data) -> None:
        docs = cls.read_all()
        docs.append(cls(**data))
        with open(f"./data/{cls.BASE}.json", "w") as file:
            json.dump(docs, file, cls=ModelEncoder, indent=2)

    @classmethod
    def read_all(cls):
        with open(f"./data/{cls.BASE}.json", "r") as file:
            return [cls(**x) for x in json.load(file)]

    def remove(self) -> None:
        docs = self.read_all()
        docs.remove(self)
        with open(f"./data/{self.BASE}.json", "w") as file:
            json.dump(docs, file, cls=ModelEncoder, indent=2)


class Collection(Model):
    def __to_dict__(self):
        data_dict = self.__dict__.copy()
        del data_dict["id"]
        return data_dict

    @classmethod
    def read(cls, id: int | str):
        try:
            with open(f"./data/{cls.BASE}/{id}.json", "r") as file:
                return cls(id=int(id), **json.load(file))
        except FileNotFoundError:
            return None

    @classmethod
    def read_all(cls):
        files = os.listdir(f"./data/{cls.BASE}")
        ids = [file[: file.index(".")] for file in files]
        return [cls.read(id) for id in ids]

    def update(self):
        with open(f"./data/{self.BASE}/{self.id}.json", "w") as file:
            json.dump(self, file, cls=ModelEncoder, indent=2)
        return self

    def delete(self):
        os.remove(f"./data/{self.BASE}/{self.id}.json")
        return self
