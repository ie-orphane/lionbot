import random
import datetime as dt
from discord.ext import tasks, commands
from utils import get_week, open_file, log
from constants import GOLDEN_RATIO, COLOR
from config import get_emoji, get_channel
from discord.channel import TextChannel


START_HOUR_UTC, START_MINUTE_UTC = 8, 30
END_HOUR_UTC, END_MINUTE_UTC = 16, 0

MIN_END_TIME = 60 * 1
MAX_END_TIME = 60 * 5


async def send_message(current_week: dict, outlist_event_channel) -> None:

    black_list_role = None

    # get Geek of the week and black list roles
    for role in outlist_event_channel.guild.roles:
        if role.name == "Black List":
            black_list_role = role

    # if not found create new one
    if not black_list_role:
        black_list_role = await outlist_event_channel.guild.create_role(
            name="Black List", color=COLOR.black
        )

    await outlist_event_channel.send(
        content=(
            f"{black_list_role.mention}, Outlist Event Started!\n"
            f"Use `/blacklist out` with only **{current_week["amout"]}** {get_emoji("coin")} to get your freedom.\n"
            f"You have only **{(current_week["ends_in"] % 3600) // 60}** minutes and **{current_week["ends_in"] % 60}** seconds until the event ends."
        )
    )


@tasks.loop(seconds=15)
async def blacklist(bot: commands.Bot):
    this_week = get_week()
    weeks = open_file("data/blacklist.json")

    if str(this_week.count) not in weeks:
        log("Task", "yellow", "Blacklist", "Initiliasing...")

        start = this_week.start_date.toordinal()
        random_ordinal = random.randint(start, start + 4)

        date = dt.date.fromordinal(random_ordinal)

        random_hour, random_minute = random.choice(
            [
                (hour, minute)
                for hour in range(START_HOUR_UTC, END_HOUR_UTC + 1)
                for minute in range(0, 60, 15)
                if (START_HOUR_UTC, START_MINUTE_UTC)
                <= (hour, minute)
                <= (END_HOUR_UTC, END_MINUTE_UTC)
            ]
        )

        time = dt.time(random_hour, random_minute)

        weeks[str(this_week.count)] = {
            "datetime": str(dt.datetime.combine(date, time, dt.UTC)),
            "amout": GOLDEN_RATIO ** ((random_ordinal - start) / 2),
            "ends_in": random.randint(MIN_END_TIME, MAX_END_TIME),
            "started": False,
            "claimed_by": None,
        }

        open_file("data/blacklist.json", weeks)

        log("Task", "green", "Blacklist", "Initiliased!")

    current_week = weeks[str(this_week.count)]

    if current_week["started"]:
        return

    now = dt.datetime.now(dt.UTC).replace(second=0, microsecond=0)
    if dt.datetime.fromisoformat(current_week["datetime"]) == now:
        log("Task", "yellow", "Blacklist", "starting...")

        if (outlist_event_channel_id := get_channel("outlist_event")) is not None:

            if (
                outlist_event_channel := bot.get_channel(outlist_event_channel_id)
            ) is not None:

                if isinstance(outlist_event_channel, TextChannel):
                    send_message(current_week, outlist_event_channel)

                else:
                    log(
                        "Error",
                        "red",
                        "OutlistEvent",
                        "outlist channel is not a TextChannel",
                    )

            else:
                log("Error", "red", "Task", "outlist event channel not found")

        else:
            log("Error", "red", "Task", "outlist event channel id not found")

        current_week["started"] = True

        open_file("data/blacklist.json", weeks)

        log("Task", "green", "Blacklist", "started!")
