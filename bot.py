import os
from dotenv import load_dotenv
from bot import Bot
from utils import log
from config import check_channels


def main():
    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    if TOKEN is None:
        log("Error", "red", "Bot", ".env missed TOKEN")
        return

    if (missing_channel := check_channels()) is not None:
        log("Error", "red", "Bot", f"missing the {missing_channel} channel")
        return

    bot = Bot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
