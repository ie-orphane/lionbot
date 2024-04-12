import json
from models.__schema__ import Data
from models.__users__ import UserData

class StudentData(UserData):
    def __to_dict__(self):
        return self.id


class ClassData(Data):
    BASE = "data/classes"
    id: str
    students: list[StudentData]

    @classmethod
    def read(cls, id: int | str):
        try:
            with open(f"{cls.BASE}/{id}.json", "r") as file:
                data: dict = json.load(file)
                data["students"] = [
                    StudentData.read(x) for x in data["students"]
                ]
                return cls(id=id, **data)
        except FileNotFoundError:
            return None
        
    def add_student(self, id: int | str):
        user = StudentData.read(id)
        if user is None:
            return False
        if user not in self.students:
            self.students.append(user)
            self.update()
        return True
