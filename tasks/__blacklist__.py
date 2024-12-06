import random
import datetime as dt
from discord.ext import tasks, commands
from utils import get_week, open_file, clr, log
from bot.config import CHANNELS, Emoji
from constants import GOLDEN_RATIO, COLOR


START_HOUR_UTC, START_MINUTE_UTC = 8, 30
END_HOUR_UTC, END_MINUTE_UTC = 16, 0

MIN_END_TIME = 60 * 1
MAX_END_TIME = 60 * 5


@tasks.loop(seconds=15)
async def blacklist(bot: commands.Bot):
    this_week = get_week()
    weeks = open_file("data/blacklist.json")

    if str(this_week.count) not in weeks:
        bot.log("Task", clr.yellow, "Blacklist", "Initiliasing...")

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

        bot.log("Task", clr.green, "Blacklist", "Initiliased!")

    current_week = weeks[str(this_week.count)]

    if current_week["started"]:
        return

    now = dt.datetime.now(dt.UTC).replace(second=0, microsecond=0)
    if dt.datetime.fromisoformat(current_week["datetime"]) == now:
        bot.log("Task", clr.yellow, "Blacklist", "starting...")

        eventchannel = bot.get_channel(CHANNELS.blacklist_event)

        black_list_role = None

        # get Geek of the week and black list roles
        for role in eventchannel.guild.roles:
            if role.name == "Black List":
                black_list_role = role

        # if not found create new one
        if not black_list_role:
            black_list_role = await eventchannel.guild.create_role(
                name="Black List", color=COLOR.black
            )

        await eventchannel.send(
            content=(
                f"{black_list_role.mention}, Outlist Event Started!\n"
                f"Use `/blacklist out` with only **{current_week["amout"]}** {Emoji.coin} to get your freedom.\n"
                f"You have only **{(current_week["ends_in"] % 3600) // 60}** minutes and **{current_week["ends_in"] % 60}** seconds until the event ends."
            )
        )

        current_week["started"] = True

        open_file("data/blacklist.json", weeks)

        bot.log("Task", clr.green, "Blacklist", "started!")
