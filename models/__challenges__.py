from models.__schema__ import Document


class ChallengeData(Document):
    BASE: str = "challenges"
    id: str
    instructions: str
    input: str
    output: str
