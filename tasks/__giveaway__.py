import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

import discord
from discord.ext import commands, tasks

import env
from config import bot as profile
from config import get_emoji
from consts import COLOR, GIVEAWAY_THRESHOLD
from models import UserData
from ui import GiveawayView
from utils import Log, month, number


@tasks.loop(minutes=45)
async def giveaway(bot: commands.Bot):
    current = month(datetime.now(UTC))
    last = month(current.datetime.replace(day=1) - timedelta(days=1))

    path = Path(env.BASE_DIR) / "data" / "giveaway.json"
    with open(path) as f:
        data = json.load(f)

    if last.id in data and data[last.id].get("ended_at") is None:
        winner = bot.user.id
        if len(data[last.id]["entrants"]) != 0:
            winner = random.choice(data[last.id]["entrants"])
        geek = None
        if winner != bot.user.id and (geek := UserData.read(winner)) is not None:
            geek.add_coins(data[last.id]["prize"], "events")
            profile.coins -= data[last.id]["prize"]

        data[last.id]["ended_at"] = str(current.datetime)
        data[last.id]["winner"] = winner

        if (
            ((message_id := (data[last.id].get("message_id"))) is not None)
            and ((channel := bot.get_listed_channel("events")) is not None)
            and ((message := await channel.fetch_message(message_id)) is not None)
        ):
            embed = message.embeds[0]
            embed.color = COLOR.blue
            msg = f"Winner: <@{data[last.id]['winner']}>"
            if geek is not None:
                msg += f" ({geek.name})"
            embed.description = embed.description.replace("Winner: **`1`**", msg)
            embed.set_footer(text=None)
            await message.edit(embed=embed, view=None)
            if winner != bot.user.id:
                await message.reply(
                    content=(
                        f"Congratulations <@{data[last.id]['winner']}>! "
                        f"You won {number(data[last.id]['prize'])} {get_emoji('coin')}."
                    )
                )
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        Log.job("GIVEAWAY", f"Winner for {last.id} is {data[last.id]['winner']}")
        return

    if current.id not in data:
        users = UserData.read_all()
        total = sum([user.coins for user in users])
        if 0 < profile.coins >= ((total / len(users)) % GIVEAWAY_THRESHOLD):
            data[current.id] = {
                "entrants": [],
                "started_at": str(current.datetime),
                "prize": profile.coins,
            }
            ends_in = int(
                (current.datetime.replace(day=1) + timedelta(days=31))
                .replace(second=0, microsecond=0, minute=0, hour=0)
                .timestamp()
            )
            if (channel := bot.get_listed_channel("events")) is not None:
                message = await channel.send(
                    embed=discord.Embed(
                        color=COLOR.yellow,
                        title=f"{current.date:%B %Y}",
                        description=(
                            f"Prize: {number(data[current.id]['prize'])} {get_emoji('coin')}\n"
                            "Entrants: **`0`**\n"
                            f"Winner: **`1`**\n"
                            f"Ends: <t:{ends_in}:R>"
                        ),
                    ).set_footer(text="Click 🎉 to enter!"),
                    view=GiveawayView(bot),
                )
                data[current.id]["message_id"] = message.id
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            Log.job("GIVEAWAY", f"Started giveaway for {current.id}")
