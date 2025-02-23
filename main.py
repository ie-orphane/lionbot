import env
from bot import Bot
from utils import Log
from config import check_config
from models.__self__ import Migration


def main():
    if env.IS_MISSING:
        return

    Migration.run()

    if (missing_message := check_config()) is not None:
        Log.error("Bot", missing_message)
        return

    Bot().run(env.DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
