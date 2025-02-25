import random
import env
import discord
import datetime as dt
from discord.ext import tasks, commands
from utils import get_week, open_file, Log, number
from consts import GOLDEN_RATIO, COLOR
from config import get_emoji
from zoneinfo import ZoneInfo
from ui import OutlistView


START_HOUR, START_MINUTE = 9, 30
END_HOUR, END_MINUTE = 17, 0

MIN_END_TIME = 60 * 1
MAX_END_TIME = 60 * 5


@tasks.loop(seconds=15)
async def outlist(bot: commands.Bot):
    this_week = get_week()
    weeks = open_file(f"{env.BASE_DIR}/data/outlist.json")

    if str(this_week.count) not in weeks:
        Log.job("Outlist", "Initiliasing...")

        start = this_week.start_date.toordinal()
        random_ordinal = random.randint(start, start + 4)

        date = dt.date.fromordinal(random_ordinal)

        random_hour, random_minute = random.choice(
            [
                (hour, minute)
                for hour in range(START_HOUR, END_HOUR + 1)
                for minute in range(0, 60, 15)
                if (START_HOUR, START_MINUTE)
                <= (hour, minute)
                <= (END_HOUR, END_MINUTE)
            ]
        )

        time = dt.time(random_hour, random_minute)

        weeks[str(this_week.count)] = {
            "started_at": str(
                dt.datetime.combine(date, time, ZoneInfo("Africa/Casablanca"))
            ),
            "amount": (GOLDEN_RATIO ** ((random_ordinal - start) / 2))
            * random.choice([3, 5, 7, 11]),
            "ends_in": random.randint(MIN_END_TIME, MAX_END_TIME),
            "started": False,
            "claimed_by": None,
        }

        open_file(f"{env.BASE_DIR}/data/outlist.json", weeks)

        Log.job("Outlist", "Initiliased!")

    current_week = weeks[str(this_week.count)]

    if current_week["started"]:
        return

    now = dt.datetime.now(ZoneInfo("Africa/Casablanca")).replace(
        second=0, microsecond=0
    )
    if dt.datetime.fromisoformat(current_week["started_at"]) == now:
        Log.job("Outlist", "starting...")

        if (events_channel := bot.get_listed_channel("events")) is None:
            return

        black_list_role = None
        for role in events_channel.guild.roles:
            if role.name == "Black List":
                black_list_role = role
        if not black_list_role:
            black_list_role = await events_channel.guild.create_role(
                name="Black List", color=COLOR.black
            )

        message = await events_channel.send(
            content=f"{black_list_role.mention}, **Outlist Event Started**!\n",
            embed=discord.Embed(
                color=COLOR.yellow,
                description=(
                    f"**Cost**: {number(current_week["amount"])} {get_emoji("coin")}\n"
                    f"**Ends**: <t:{int((dt.datetime.now(ZoneInfo("Africa/Casablanca")) + dt.timedelta(seconds=current_week["ends_in"])).timestamp())}:R>\n"
                ),
            ),
            view=OutlistView(bot, current_week["ends_in"]),
        )

        current_week["started"] = True
        current_week["message_id"] = message.id

        open_file(f"{env.BASE_DIR}/data/outlist.json", weeks)

        Log.job("Outlist", "started!")
