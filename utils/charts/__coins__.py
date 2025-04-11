import datetime as dt
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import env
from consts import COLOR
from models import UserData

from .__self__ import lighten_color

matplotlib.use("Agg")


__all__ = ["coins_bar", "coins_line"]


def coins_bar(users: list[UserData]) -> str:
    r"""
    Create a bar chart of the number of users with each coin amount.
    Args:
        users (list[UserData]): List of user data models.
    Returns:
        str: Path to the saved bar chart image.
    """
    name = f"{env.BASE_DIR}/storage/images/coins_bar.png"

    coin_counts = Counter([int(user.coins) for user in users])
    coin_values = [coin for coin in sorted(coin_counts.keys()) if coin_counts[coin] > 0]
    counts = [coin_counts[coin] for coin in coin_values]

    fig, axs = plt.subplots(sharey=True)

    axs.bar(coin_values, counts, color="black", edgecolor="black")

    for spine in axs.spines.values():
        spine.set_visible(False)

    axs.tick_params(axis="x", length=0)
    axs.tick_params(axis="y", length=0)

    axs.yaxis.set_major_locator(MaxNLocator(integer=True))

    fig.savefig(name, format="png")
    plt.close(fig)

    return name


def coins_line(users: list[UserData]) -> str:
    r"""
    Create a line plot of the total number of coins over time.
    Args:
        users (list[UserData]): List of user data models.
    Returns:
        str: Path to the saved line plot image.
    """
    name = f"{env.BASE_DIR}/storage/images/coins_line.png"

    with open(f"{env.BASE_DIR}/data/transactions.csv") as f:
        context = f.readlines()
    lines = [line[:-1].split(",")[:5] for line in context]

    data = {}
    for datetime, user_id, current, operation, amount, *_ in lines[1:]:
        date = datetime[:10]
        data.setdefault(date, {})
        data[date][int(user_id)] = (
            float(current) + float(amount)
            if operation == "add"
            else float(current) - float(amount)
        )
    users = {user.id: user.coins for user in users}

    today = dt.date.today()
    data = sorted(data.items(), key=lambda x: dt.date.fromisoformat(x[0]), reverse=True)
    days = [day[0] for day in data]
    data = [day[1] for day in data]

    index = 0
    count = 11
    max_days = len(days)
    day = today
    all_days = []
    all_coins = []
    while True:
        if str(day) in days:
            index += 1
            if index >= max_days or index >= count:
                break
            users.update(data[index])
        all_days.append(f"{day.month}/{day.day}")
        all_coins.append(sum(users.values()))
        day -= dt.timedelta(days=1)
    all_coins.reverse()
    all_days.reverse()

    fig, ax = plt.subplots()

    ax.fill_between(all_days, all_coins, color=lighten_color(COLOR.yellow), alpha=0.25)
    ax.plot(
        all_days,
        all_coins,
        linewidth=1.25,
        markersize=3,
        color=lighten_color(COLOR.yellow, 0),
        alpha=0.75,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_alpha(0.25)
    ax.spines["left"].set_alpha(0.25)
    ax.spines["right"].set_visible(False)

    ax.grid(True, alpha=0.25)
    ax.tick_params(axis="x", colors=(0, 0, 0, 0.5))
    ax.tick_params(axis="y", colors=(0, 0, 0, 0.5))

    ax.set_ylim(bottom=min(all_coins), top=max(all_coins))
    ax.set_xticks(all_days[::2])

    fig.savefig(name, format="png")
    plt.close(fig)

    return name
