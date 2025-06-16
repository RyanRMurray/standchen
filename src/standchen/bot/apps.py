import asyncio
from django.apps import AppConfig

import logging

import discord
from discord.ext.commands import Bot

from standchen.bot.bot_settings import SETTINGS
from standchen.bot.core_commands import StandchenBotCore

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
discord.utils.setup_logging(level=logging.INFO, root=False)

discord_bot = Bot(command_prefix="$", intents=intents)
discord_bot_coro = None


async def start_bot() -> bool:
    global discord_bot
    global discord_bot_coro
    if discord_bot_coro is None:
        await discord_bot.add_cog(StandchenBotCore(), guild=SETTINGS.guild)
        discord_bot_coro = asyncio.create_task(
            asyncio.to_thread(discord_bot.run(SETTINGS.bot_token))
        )
        return True
    else:
        return False
    # await discord_bot.start(SETTINGS.bot_token)


@discord_bot.event
async def on_ready():
    logging.info(f"Discord Bot logged in as {discord_bot.user}")

    synced = await discord_bot.tree.sync(guild=SETTINGS.guild)
    logging.info(f"Synced command tree. {len(synced)} commands loaded.")


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "standchen.bot"
