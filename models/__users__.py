from models.__schema__ import Data


class UserData(Data):
    BASE = "users"
    id: int
    name: str
    coins: int
    token: str
    github: str
    portfolio: str
    training: str
