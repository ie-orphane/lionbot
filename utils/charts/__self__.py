def lighten_color(color: int | str, /, factor: float = 0.5) -> str:
    if isinstance(color, str):
        color = color.lstrip("#")
    elif isinstance(color, int):
        color = hex(color).lstrip("0x").ljust(6, "0")
    else:
        raise TypeError(f"color must be int or str not {type(color).__dict__}")

    r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)

    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)

    return f"#{r:02x}{g:02x}{b:02x}"
