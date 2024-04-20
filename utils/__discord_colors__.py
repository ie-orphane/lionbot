import discord

COLORS = {
    "indigo": "#6610f2",
    "purple": "#6f42c1",
    "pink": "#d63384",
    "red": "#dc3545",
    "orange": "#fd7e14",
    "yellow": "#ffc107",
    "green": "#198754",
    "teal": "#20c997",
    "cyan": "#0dcaf0",
    "black": "#000",
    "white": "#fff",
    "gray": "#6c757d",
}

all = []
for name, color in COLORS.items():
    exec(
        f"{name} = discord.Colour.from_str('{color}').value; all.append({name})"
    )
