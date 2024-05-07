import os
from dotenv import load_dotenv
from bot import Bot


def main():
    load_dotenv()
    TOKEN = os.getenv("TOKEN")

    bot = Bot()
    if TOKEN:
        bot.run(TOKEN)
    else:
        bot.log("Error", "Bot", ".env missed TOKEN")


if __name__ == "__main__":
    main()
