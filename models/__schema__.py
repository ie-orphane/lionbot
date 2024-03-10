import json, os

class Model:
    def __init__(self, **kwargs) -> None:
        self.__dict__ = kwargs

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.__dict__}"

    def __to_dict__(self):
        return self.__dict__


class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.__to_dict__()
        return json.JSONEncoder.default(self, obj)


class Data(Model):
    def __to_dict__(self):
        data_dict = self.__dict__
        del data_dict["id"]
        return data_dict

    @classmethod
    def read(cls, id: int | str):
        try:
            with open(f"{cls.BASE}/{id}.json", "r") as file:
                return cls(id=int(id), **json.load(file))
        except FileNotFoundError:
            return None

    @classmethod
    def read_all(self):
        files = os.listdir(self.BASE)
        ids = [file[: file.index(".")] for file in files]
        return [self.read(id) for id in ids]

    def update(self):
        with open(f"{self.BASE}/{self.id}.json", "w") as file:
            json.dump(self, file, cls=ModelEncoder, indent=2)
