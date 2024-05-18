from models.__schema__ import Collection, Relation
from models.__challenges__ import ChallengeData, ChallengeFields
import random
from datetime import datetime, UTC
from utils import RANKS


class UserChallenge(Relation, ChallengeFields):
    MODEL = ChallengeData
    requested: datetime
    submited: datetime = None
    approved: datetime = None


class UserData(Collection):
    BASE = "users"
    id: int
    name: str
    coins: int
    points: int
    token: str
    github: str
    portfolio: str
    training: str
    _challenges: dict[str, dict]
    graduated: bool

    @property
    def master_message(self):
        return random.choice(
            [
                "New champion crowned! You've conquered every challenge!",
                "The challenges are weeping - you've defeated them all!",
                "100% complete! You've conquered every challenge!",
                "No challenge was a match for you - you finished them all!",
                "Domination achieved! You've completed every single challenge!",
                "You've officially graduated from challenge-land!",
                "You did it! All challenges conquered!",
                "Challenge master alert! You've completed everything!",
                "High fives all around - you finished all the challenges!",
            ]
        )

    @property
    def approve_message(self):
        return random.choice(
            [
                "**Congrats!** Your code just passed the test with **flying bytes**?\nYou're ready to **tackle** the challenge!",
                "**Level Up!** Your code has been approved.\nGet ready for the **next challenge**!",
                "> ❛**The only way to do great work is to love what you do.**❜\n> - Steve Jobs\n**We see your dedication!** Code has been approved",
                "We see all the **hard work** you put into **your code**.\n**Challenge** has been approved. Keep up the **good work**!",
            ]
        )

    @property
    def rank(self):
        for rank, data in list(RANKS.items())[::-1]:
            if self.points >= data.required_points:
                return rank

    @property
    def challenges(self):
        return [
            UserChallenge(challenge_id, **challenge_data)
            for challenge_id, challenge_data in self._challenges.items()
        ]

    @property
    def current_challenge(self) -> UserChallenge | None:
        for challenge in self.challenges:
            if challenge.approved is None:
                return challenge

    def request_challenge(self):

        if not self._challenges:
            challenge = ChallengeData.read(308082)
            self._challenges.update(
                {challenge.id: {"requested": str(datetime.now(UTC))}}
            )
            self.update()
            return challenge

        all_challanges = ChallengeData.read_all()

        challenges = [
            challenge_data
            for challenge_data in all_challanges
            if challenge_data.rank == self.rank
        ]

        if len(challenges) == len(all_challanges):
            return None

        challenge = random.choice(
            [
                challenge
                for challenge in challenges
                if str(challenge.id) not in self._challenges.keys()
            ]
        )
        self._challenges.update({challenge.id: {"requested": str(datetime.now(UTC))}})
        self.update()
        return challenge

    def get_challenge(self, challenge_id: str | int):
        try:
            challenge_data = self._challenges[str(challenge_id)]
            return UserChallenge(challenge_id, **challenge_data)
        except KeyError:
            return None
