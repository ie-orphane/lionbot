import matplotlib.pyplot as plt
import matplotlib
from consts import COLOR

__all__ = ["leaderboard", "answers"]


def lighten_color(color: int | str, /, factor: float = 0.5) -> str:
    if isinstance(color, str):
        color = color.lstrip("#")
    elif isinstance(color, int):
        color = hex(color).lstrip("0x").ljust(6, "0")
    else:
        raise TypeError(f"color must be int or str not {type(color).__dict__}")

    r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)

    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)

    return f"#{r:02x}{g:02x}{b:02x}"


def answers(answers: dict[str, int], colors: list[bool], filename: str) -> None:
    try:
        fig, ax = plt.subplots(figsize=(3, 2.5))
    except AttributeError:
        matplotlib.use("Agg")
        fig, ax = plt.subplots(figsize=(3, 2.5))

    colors = [
        lighten_color(COLOR.yellow, 0.25) if color else lighten_color(COLOR.gray, 0.825)
        for color in colors
    ]

    container = ax.bar(answers.keys(), answers.values(), color=colors)
    ax.bar_label(container, label_type="edge", padding=6)

    ax.yaxis.set_visible(False)
    for position in ("left", "right", "top"):
        ax.spines[position].set_visible(False)


    fig.savefig(f"assets/images/{filename}.png", format="png", dpi=150)
    plt.close(fig)
