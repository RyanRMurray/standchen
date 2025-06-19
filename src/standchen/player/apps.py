import asyncio
import logging
from typing import List
import discord
from django.apps import AppConfig
from discord.ext.commands import Bot
from threading import Thread
from standchen.player.bot.bot_settings import SETTINGS

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


standchen_player = None


async def set_vc(sender, **kwargs):
    await standchen_player.set_vc(kwargs["voice_channel"])


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


class PlayerThread(Thread):
    def run(self):
        global standchen_player
        asyncio.run(standchen_player.execute())


class BotThread(Thread):
    async def add_cog(self):
        from standchen.player.bot.core_commands import StandchenBotCore

        await discord_bot.add_cog(StandchenBotCore(), guild=SETTINGS.guild)

    def run(self):
        asyncio.run(self.add_cog())
        discord_bot.run(SETTINGS.bot_token)


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "standchen.player"
    threads: List[Thread] = [BotThread(), PlayerThread()]

    def ready(self):
        from standchen.player.models import StandchenPlayer

        global standchen_player
        standchen_player = StandchenPlayer()

        # start bot and player
        self.threads[0].start()  # bot
        self.threads[1].start()  # player
