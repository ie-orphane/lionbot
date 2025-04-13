import json
import os
import pprint
from typing import Any, List, Self

import env


class Model:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {pprint.saferepr(object=self.__dict__)}"

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__

    def __to_dict__(self):
        return self.__dict__


class Relation(Model):
    def __init__(self, id: str | int, **kwargs) -> None:
        self.__dict__.update({**kwargs, **self.MODEL.read(id).__dict__})


class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.__to_dict__()
        return json.JSONEncoder.default(self, obj)


class Document(Model):
    @staticmethod
    def __write(obj: Any, fp: str) -> None:
        with open(f"{env.BASE_DIR}/data/{fp}", "w") as file:
            json.dump(obj, file, cls=ModelEncoder, indent=2)

    @classmethod
    def exists(cls: Self, id: str) -> bool:
        docs = [data.id for data in cls.read_all()]
        return id in docs

    @classmethod
    def create(cls: Self, **data) -> Self:
        docs = cls.read_all()
        doc = cls(**data)
        docs.append(doc)
        cls.__write(docs, f"{cls.BASE}.json")
        return doc

    @classmethod
    def read_all(cls: Self) -> List[Self]:
        with open(f"{env.BASE_DIR}/data/{cls.BASE}.json") as file:
            return [cls(**x) for x in json.load(file)]

    def remove(self) -> Self:
        docs = self.read_all()
        docs.remove(self)
        self.__write(docs, f"{self.BASE}.json")
        return self


class Collection(Model):
    def __to_dict__(self):
        data_dict = self.__dict__.copy()
        del data_dict["id"]
        return data_dict

    @classmethod
    def read(cls: Self, id: int | str) -> Self | None:
        try:
            with open(f"{env.BASE_DIR}/data/{cls.BASE}/{id}.json") as file:
                return cls(id=int(id), **json.load(file))
        except FileNotFoundError:
            return None

    @classmethod
    def __get_ids(cls: Self) -> List[str]:
        return [
            filename[: filename.index(".")]
            for filename in os.listdir(f"{env.BASE_DIR}/data/{cls.BASE}")
        ]

    @classmethod
    def read_all(cls: Self) -> List[Self]:
        return [cls.read(id) for id in cls.__get_ids()]

    @classmethod
    def exits(cls: Self, id: str | int) -> bool:
        return str(id) in cls.__get_ids()

    def update(self) -> Self:
        with open(f"{env.BASE_DIR}/data/{self.BASE}/{self.id}.json", "w") as file:
            json.dump(self, file, cls=ModelEncoder, indent=2)
        return self

    def delete(self) -> Self:
        os.remove(f"{env.BASE_DIR}/data/{self.BASE}/{self.id}.json")
        return self
