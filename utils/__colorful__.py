from typing import Callable

__all__ = ["Color"]

RESET = "\x1b[0m"
BOLD = "\x1b[1m"

COLORS = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


class Color:
    RESET = RESET
    BOLD = BOLD
    black: Callable[[str], str]
    red: Callable[[str], str]
    green: Callable[[str], str]
    yellow: Callable[[str], str]
    blue: Callable[[str], str]
    magenta: Callable[[str], str]
    cyan: Callable[[str], str]
    white: Callable[[str], str]


for i in range(8):
    exec(f"Color.{COLORS[i]} = lambda text: f'{BOLD}\x1b[3{i}m{"{text}"}{RESET}'")
    exec(f"Color._{COLORS[i]} = lambda text: f'\x1b[3{i}m{"{text}"}{RESET}'")
    exec(f"Color.{COLORS[i].upper()} = f'\x1b[3{i}m'")
