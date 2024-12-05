import os
from dotenv import load_dotenv
from bot import Bot
from utils import clr


def main():
    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    if TOKEN is None:
        bot.log("Error", clr.red, "Bot", ".env missed TOKEN")
        return

    bot = Bot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
