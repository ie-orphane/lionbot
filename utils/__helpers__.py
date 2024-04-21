import pickle
import json
import os
from datetime import datetime, timedelta, date, UTC
import matplotlib.pyplot as plt
from utils import clr
from typing import Literal


def log(type: Literal["Info", "Error", "Task"], func, name: str, message: str):
    log_time = clr.black(datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))

    return f"{log_time} {func(type)}    {clr.magenta(name)} {message}"


def get_files(path: str, praser=int):
    return [praser(file[: file.index(".")]) for file in os.listdir(path)]


def open_file(file_path, data=None):
    file_extention = file_path.split(".")[-1]
    match file_extention:
        case "json":
            module = json
            write_mode = "w"
            read_mode = "r"
        case "pickle":
            module = pickle
            write_mode = "wb"
            read_mode = "rb"

    if data:
        with open(file_path, write_mode) as file:
            if file_extention == "json":
                module.dump(data, file, indent=2)
            else:
                module.dump(data, file)
            return

    with open(file_path, read_mode) as file:
        return module.load(file)


class Week:
    count: int
    start_date: date
    end_date: date

    def __init__(self, data: dict) -> None:
        self.__dict__ = data
        self.readable_start = str(self.start_date)
        self.readable_end = str(self.end_date)
        self.human_readable_start = f"{self.start_date:%d %b %Y}"
        self.human_readable_end = f"{self.end_date:%d %b %Y}"


def get_week(*, week_argument="last", end_date=None) -> Week | list:
    start_date = datetime(2023, 10, 23)
    end_date = end_date or datetime.utcnow()
    weeks: list[Week] = []

    current_date = start_date
    week_count = 1

    while current_date <= end_date:
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        weeks.append(
            Week(
                {
                    "count": week_count,
                    "start_date": start_of_week.date(),
                    "end_date": end_of_week.date(),
                }
            )
        )

        current_date += timedelta(days=7)
        week_count += 1

    match week_argument:
        case "beforelast":
            last_week = weeks[-2]
            return last_week
        case "last":
            last_week = weeks[-1]
            return last_week
        case "all":
            return weeks
        case _:
            return weeks[int(week_argument) - 1]


def leaderboard_image(template: str, image: str, data: list, **heading_data: dict):
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

    # setting variables
    w = 785
    h = 43 * len(data)
    rows = len(data) + 2  # number of rows that we want
    cols = 8  # number of columns that we want

    # setting structure
    fig, ax = plt.subplots(facecolor=background_color)
    fig.set_size_inches(w / 100, h / 100)

    ax.set_ylim(ybottom, rows)  #  y limits
    ax.set_xlim(0, cols)  #  X limits

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    ax.axis("off")  # removing all the spines

    # iterating over each row of the dataframe and plot the text #FFD700 #CD7F32 #C0C0C0
    for index, user in enumerate(data[::-1]):
        # ploting all data
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

    # Adding the headers
    for xpos, name in [
        (0.5, ""),
        (0.75, "Coder"),
        (2.875, "Total"),
        (4.25, "Languages"),
    ]:
        ax.text(xpos, rows - 1 + x, name, weight="bold", size=11, color=text_color)

    # Adding heading (title / footenote)
    exec(heading)

    # adds main line below the headers
    ax.plot(
        [0.25, cols - 0.25],
        [rows - 1.375 + x, rows - 1.375 + x],
        ls="-",
        lw=1,
        c=text_color,
    )

    # adds main line below the data
    ax.plot([0.25, cols - 0.25], [0.5 + x, 0.5 + x], ls="-", lw=1, c=text_color)

    # adds multiple lines below each row
    for index in range(len(data)):
        if index != 0:
            ax.plot(
                [0.25, cols - 0.2],
                [index + 0.5 + x, index + 0.5 + x],
                ls="-",
                lw=".375",
                c=text_color,
            )

    # save the figure as an image
    fig.savefig(f"./assets/images/{image}_{template}_leaderboard.png", format="png")

    plt.close(fig)
