class Rank:
    name: str
    difficulty: str
    coins: int
    points: int
    required_points: int

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        return f"Rank {self.__dict__}"


RANKS = {
    rank: Rank(
        **{
            "coins": 6.9 * index,
            "points": 25 * index,
            "difficulty": difficulty,
            "required_points": required_points,
        }
    )
    for index, (rank, difficulty, required_points) in enumerate(
        [
            ("apprentice", "easy", 0),
            ("knight", "normal", 100),
            ("wizard", "medium", 250),
        ],
        1,
    )
}
