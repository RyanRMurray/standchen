import json
import os
from pathlib import Path

import discord

os.environ.setdefault("STANDCHEN_SETTINGS", "./settings.json")


class Settings:
    guild: discord.Object
    bot_token: str

    def __init__(self, j):
        self.guild = discord.Object(j["guild_id"])
        self.bot_token = j["bot_token"]


def load_settings(path: Path) -> Settings:
    """Loads settings file and makes it available as an attribute."""

    if not path.is_file():
        raise Exception(f"File not found: {path}")

    j = None
    with open(path, "r") as f:
        j = json.load(f)

    return Settings(j)


SETTINGS = load_settings(Path(os.environ.get("STANDCHEN_SETTINGS")))
