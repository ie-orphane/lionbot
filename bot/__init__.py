import config
from utils import Log
from discord import TextChannel
from .__discord__ import DiscordBot
from .__embeds__ import BotEmbeds


class Bot(DiscordBot, BotEmbeds):
    def get_listed_channel(
        self, channel_name: str, is_text_channel: bool = True
    ) -> TextChannel | None:
        if (channel_id := config.get_channel(channel_name)) is None:
            Log.error("Bot", f"{channel_name}: channel id not found")
            return None

        if (channel := self.get_channel(channel_id)) is None:
            Log.error("Bot", f"{channel_name}: channel not found")
            return None

        if is_text_channel:
            if not isinstance(channel, TextChannel):
                Log.error("Bot", f"{channel_name}: channel is not a TextChannel")
                return None

        return channel
