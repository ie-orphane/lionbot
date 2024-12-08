import os
from dotenv import load_dotenv
from bot import Bot
from utils import Log
from config import check_config


def main():
    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    if TOKEN is None:
        Log.error("Bot", ".env missed TOKEN")
        return

    if (missing_message := check_config()) is not None:
        Log.error("Bot", missing_message)
        return

    bot = Bot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
