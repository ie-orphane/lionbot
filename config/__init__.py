from .__self__ import *
from .__channels__ import *
from .__emojis__ import *
from .__extensions__ import *
from .__users__ import *
from .__messages__ import *


def check_config() -> str | None:
    if (missing_channel := check_channels()) is not None:
        return f"missing the {missing_channel} channel"

    if get_config("GUILD") is None:
        return f"missing the GUILD field"
