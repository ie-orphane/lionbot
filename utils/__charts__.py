import env
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


async def answers(answers: dict[str, int], colors: list[bool], filename: str) -> None:
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

    fig.savefig(f"{env.BASE_DIR}/storage/images/{filename}.png", format="png", dpi=150)
    plt.close(fig)


async def leaderboard(template: str, image: str, data: list, **heading_data: dict):
    text_color = "white"
    background_color = "black"

    match template:
        case "top":
            ybottom = -0.5
            x = -1
            heading = f"ax.set_title('Week {heading_data['count']}  -  {heading_data['start']}  ~ {heading_data['end']}', pad=0, loc='center', va='top', fontsize=13, weight='bold', color=text_color)"

        case "bottom":
            ybottom = -1
            x = 0
            heading = f"plt.figtext(.5, .1, 'Last Update  -  {heading_data['time']}', fontsize=7.5,  ha='center', color=text_color)"

        case "middle":
            ybottom = -1
            x = 0
            heading = f""

    w = 785
    h = 43 * len(data)
    rows = len(data) + 2
    cols = 8

    try:
        fig, ax = plt.subplots(facecolor=background_color)
    except AttributeError:
        matplotlib.use("Agg")
        fig, ax = plt.subplots(facecolor=background_color)

    fig.set_size_inches(w / 100, h / 100)

    ax.set_ylim(ybottom, rows)
    ax.set_xlim(0, cols)

    fig.subplots_adjust(bottom=0.06, top=0.94)
    ax.axis("off")

    for index, user in enumerate(data[::-1]):
        for xpos, name in [
            (0.5, ""),
            (0.75, "Coder"),
            (2.875, "Total"),
            (4.25, "Languages"),
        ]:
            ax.text(
                x=xpos,
                y=index + 1 + x,
                s=user[name],
                va="center",
                color=text_color,
                size=8.5 if name == "Coder" else 9.5,
                weight="bold" if name == "Coder" else "normal",
                ha="center" if name == "" else "left",
            )

    for xpos, name in [
        (0.5, ""),
        (0.75, "Coder"),
        (2.875, "Total"),
        (4.25, "Languages"),
    ]:
        ax.text(xpos, rows - 1 + x, name, weight="bold", size=11, color=text_color)

    exec(heading)
    ax.plot(
        [0.25, cols - 0.25],
        [rows - 1.375 + x, rows - 1.375 + x],
        ls="-",
        lw=1,
        c=text_color,
    )

    ax.plot([0.25, cols - 0.25], [0.5 + x, 0.5 + x], ls="-", lw=1, c=text_color)
    for index in range(len(data)):
        if index != 0:
            ax.plot(
                [0.25, cols - 0.2],
                [index + 0.5 + x, index + 0.5 + x],
                ls="-",
                lw=".375",
                c=text_color,
            )

    fig.savefig(
        f"{__import__("env").BASE_DIR}/storage/images/{image}_{template}_leaderboard.png",
        format="png",
    )
    plt.close(fig)
