import asyncio
from django.apps import AppConfig

import logging

import discord
from discord.ext.commands import Bot

from standchen.bot.bot_settings import SETTINGS
from threading import Thread

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True

discord_bot = Bot(command_prefix="$", intents=intents)
discord_bot_coro = None


@discord_bot.event
async def on_ready():
    logging.info(f"Discord Bot logged in as {discord_bot.user}")

    synced = await discord_bot.tree.sync(guild=SETTINGS.guild)
    logging.info(f"Synced command tree. {len(synced)} commands loaded.")


class BotThread(Thread):
    async def add_cog(self):
        from standchen.bot.core_commands import StandchenBotCore

        await discord_bot.add_cog(StandchenBotCore(), guild=SETTINGS.guild)

    def run(self):
        asyncio.run(self.add_cog())
        discord_bot.run(SETTINGS.bot_token)


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "standchen.bot"

    def ready(self):
        BotThread().start()
