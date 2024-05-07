from models.__schema__ import Collection
from models.__challenges__ import ChallengeData
import random

class UserData(Collection):
    BASE = "users"
    id: int
    name: str
    coins: int
    token: str
    github: str
    portfolio: str
    training: str

    @property
    def random_challenge(self):
        return random.choice(ChallengeData.read_all())
