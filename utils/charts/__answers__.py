import matplotlib
import matplotlib.pyplot as plt

import env
from consts import COLOR

from .__self__ import lighten_color

matplotlib.use("Agg")


__all__ = ["answers"]


async def answers(answers: dict[str, int], colors: list[bool], filename: str) -> None:
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

    fig.savefig(f"{env.BASE_DIR}/storage/images/{filename}.png", format="png", dpi=150)
    plt.close(fig)
