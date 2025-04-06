import inspect
from types import MappingProxyType


__NAME__ = "CONTEXT"


class ctx:
    def __init__(
        self, *, name, func, args: MappingProxyType[str, inspect.Parameter], desc: str
    ):
        self.args: dict[str, inspect.Parameter] = {
            name: param
            for name, param in args.items()
            if name not in ("message", "bot")
        }
        self.func = func
        self.name = name
        self.desc = desc

    @property
    def usage(self) -> str:
        usage = f"**`>{self.name}`**"
        if self.args:
            usage += " " + " ".join(
                f"`{name}:{param.annotation.__name__}`"
                for name, param in self.args.items()
            )
        return usage

    async def __call__(self, **options):
        return await self.func(**options)
