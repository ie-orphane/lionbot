from models.__schema__ import Collection


class ChallengeFields:
    id: str
    instructions: str
    input: str = None
    output: str
    coins: int
    points: int


class ChallengeData(Collection, ChallengeFields):
    BASE: str = "challenges"
