from .__self__ import get_config, set_config

__all__ = ["bot"]


class _coins(type):
    @property
    def coins(cls):
        return get_config("COINS", "bot")

    @coins.setter
    def coins(cls, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError(
                f"coins must be a float instead of {value.__class__.__name__}"
            )
        set_config("COINS", value, "bot")


class bot(metaclass=_coins):
    pass
