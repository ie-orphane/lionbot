import env
from bot import Bot
from utils import Log
from config import check_config


def main():
    if env.IS_MISSING:
        return

    if (missing_message := check_config()) is not None:
        Log.error("Bot", missing_message)
        return

    bot = Bot()
    bot.run(env.TOKEN)


if __name__ == "__main__":
    main()
