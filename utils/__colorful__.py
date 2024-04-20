RESET = "\x1b[0m"
BOLD = "\x1b[1m"

COLORS = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

for i in range(8):
    exec(f"{COLORS[i]} = lambda text: f'{BOLD}\x1b[3{i}m{"{text}"}{RESET}'")
