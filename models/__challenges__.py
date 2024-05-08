from models.__schema__ import Collection


class ChallengeFields:
    id: str
    instructions: str
    input: str = None
    output: str
    reward: int


class ChallengeData(Collection, ChallengeFields):
    BASE: str = "challenges"
