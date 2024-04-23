from models.__schema__ import Collection


class UserData(Collection):
    BASE = "users"
    id: int
    name: str
    coins: int
    token: str
    github: str
    portfolio: str
    training: str
