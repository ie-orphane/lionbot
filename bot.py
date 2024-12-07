import os
from dotenv import load_dotenv
from bot import Bot
from utils import log
from config import check_config


def main():
    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    if TOKEN is None:
        log("Error", "red", "Bot", ".env missed TOKEN")
        return

    if (missing_message := check_config()) is not None:
        log("Error", "red", "Bot", missing_message)
        return

    bot = Bot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
