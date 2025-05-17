from .__challenges__ import *
from .__challenges__ import challenge as ChallengeConfig
from .__channels__ import *
from .__cooldowns__ import *
from .__emojis__ import *
from .__messages__ import *
from .__self__ import *
from .__users__ import *
from .__bot__ import *


def check_config() -> str | None:
    if (missing_channel := check_channels()) is not None:
        return f"missing the {missing_channel} channel"

    if get_config("GUILD") is None:
        return f"missing the GUILD field"
