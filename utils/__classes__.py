import random
from datetime import UTC, datetime

__all__ = [
    "number",
    "month",
    "Color",
    "Message",
    "RelativeDateTime",
]


class number(float):
    def __str__(self):
        return "**{0}**.{1}".format(
            *(super().__format__("_").replace("_", " ").split("."))
        ).removesuffix(".0")


class month:
    def __init__(self, _datetime: datetime):
        self.datetime = _datetime
        self.date = _datetime.date()
        self.id = f"{self.date:%Y-%m}"

    def __repr__(self):
        return f"month({self.date})"

    @classmethod
    def current(cls):
        return cls(datetime.now(UTC))


class Color:
    def __init__(self) -> None:
        self.indigo = 0x6610F2
        self.purple = 0x6F42C1
        self.pink = 0xD63384
        self.red = 0xDC3545
        self.orange = 0xFD7E14
        self.yellow = 0xFFC107
        self.green = 0x198754
        self.teal = 0x20C997
        self.cyan = 0x0DCAF0
        self.black = 0x000
        self.white = 0xFFF
        self.gray = 0x6C757D
        self.blue = 0x2563EB


class Message:
    @property
    def finishing(self):
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
    def waiting(self):
        return random.choice(
            [
                "is taking its sweet time. Just like a good friend! ☕",
                "is playing hard to get. But we'll win it over eventually. 😉",
                "is on its way to stardom! 🌟",
                "is safe and sound. Just a little busy. 🤗",
                "solution is out of this world! 👽",
                "is taking a nap. Don't worry, it'll wake up soon. 😴",
                "is playing hide-and-seek. Can you find it? 🔍",
                "is on the edge of a cliff. Will it fall or fly? 🪂",
            ]
        )

    @property
    def submiting(self):
        return random.choice(
            [
                "solution submitted. Awaiting evaluation. ⏳",
                "completed and sent for review. Thanks for participating! 👍",
                "is off to find its forever home. Wish it luck! 🚀",
                "solution sent. Fingers crossed! 🤞",
                "completed and submitted. Looking forward to the results! 🏆",
                "is free at last! 🕊️",
            ]
        )

    @property
    def failing(self):
        return random.choice(
            [
                "**Keep trying!** Everyone makes mistakes. 😕",
                "**Don't be discouraged!** Learning from failures is essential. 💡",
                "**Keep going!** You'll get there eventually. 👍",
                "**Don't give up!** You're closer than you think. 🏁",
                "**Keep going!** You're making progress.  📈",
                "**You've got this!** Just keep trying. 👊",
                "**Don't give up!** Keep practicing and you'll get there. 💪",
                "**Don't be discouraged!** This is just a learning opportunity. 🥊",
            ]
        )

    @property
    def succeeding(self):
        return random.choice(
            [
                "**Congratulations!** You've conquered the challenge! 🏆",
                "**Well done!** Your solution is a masterpiece! 🎨",
                "**Amazing job!** You've nailed the challenge. 🎉",
                "**Champion!** Your solution is top-notch. 🥇",
                "**You did it!** Your skills are impressive. 👏",
                "**Extraordinaire!** Your solution is out of this world. 🚀",
                "**Maestro!** Your code is music to our ears. 🎶",
                "**Legend!** Your solution is the stuff of legends. 👑",
                "**Superstar!** You've reached new heights. 🌟",
                "**Champion!** Your victory is well-deserved. 🏅",
            ]
        )

    @property
    def donation(self):
        return random.choice(
            [
                'git commit -m "feat: generous donation received 🙌" -m "Thanks a ton!"',
                'print("Thanks for the 💸! — You rock! 🤘")',
                "You're officially a part of our contributors array! 🎉",
                "Gratitude.exe running… ⚙️ Thanks for the 💰!",
                "Thanks for the support, code champion! 🧑‍💻",
                "Thanks for the 💸! Our repo loves you! 💖",
                "404: Words not found 😅 Just… thank you! 🙏",
                "Thanks! You just added a feature to our day! 🚀",
                "You’re the semicolon to our syntax — thanks! 😄;",
                "git push donation && git merge thanks 💾💜",
            ]
        )


class RelativeDateTime:

    def __init__(self, dt_str: str) -> str:
        dt = datetime.fromisoformat(dt_str)
        now = datetime.now(UTC)
        delta = now - dt
        self.day = delta.days
        self.sec = delta.seconds
        self.year, self.day = divmod(self.day, 365)
        self.month, self.day = divmod(self.day, 30)
        self.hr, self.sec = divmod(self.sec, 3600)
        self.min, self.sec = divmod(self.sec, 60)

    @property
    def pretty(self):
        for period in ["year", "month", "day", "hr", "min", "sec"]:
            n = getattr(self, period)
            if n >= 1:
                return f"{n} {period}{'s'if n > 1 else ''} ago"
        return "now"
