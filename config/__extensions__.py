from .__self__ import get_config


__all__ = ["get_extension"]


def get_extension(extension: str) -> str:
    extensions: dict[str, str] = get_config("EXTENSIONS")
    if extensions is None:
        log("Error", "red", "Config", "EXTENSIONS field not found")
        return extension
    return extensions.get(extension, extension)
