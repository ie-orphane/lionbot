import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


__all__ = ["leaderboard"]


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
