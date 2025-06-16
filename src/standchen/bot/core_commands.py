"""Core functionality for the discord bot
- Play a local file
- ping bot to see if it is operational
"""

from typing import Optional

from discord import app_commands
from discord.ext.commands import Cog
from discord.interactions import Interaction

from standchen.signals import SET_VC


class StandchenBotCore(Cog, name="Standchen Discord core functionality"):
    async def cog_load(self):
        print("Standchen Discord bot functions added:")
        for command in self.get_app_commands():
            print(command.name)

    async def ensure_vc(self, interaction: Interaction) -> Optional[str]:
        user_voice = interaction.user.voice

        if not user_voice:
            return "No voice channel detected - join a voice channel and try again."

        await SET_VC.asend(sender=self.__class__, voice_channel=user_voice)

        return

    @app_commands.command(description="check bot is alive")
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message("Pong!")

    # @app_commands.command()
    # async def pause(self, interaction: Interaction):
    #     if self.client.voice_client:
    #         self.client.voice_client.pause()

    #     await interaction.response.send_message("Paused")

    # @app_commands.command()
    # async def resume(self, interaction: Interaction):
    #     if self.client.voice_client:
    #         self.client.voice_client.resume()
    #     await interaction.response.send_message("Resumed")

    @app_commands.command(description="Add a local file to the queue.")
    async def queue(self, interaction: Interaction, filepath: str):
        await self.ensure_vc(interaction)

        # msg = await self.client.queue_local(filepath)
        # await interaction.response.send_message(msg)

        # @app_commands.command(
        #     description="Set whether to repeat a single track, a queue, or not at all."
        # )
        # @app_commands.choices(
        #     setting=[
        #         app_commands.Choice(name="None", value=1),
        #         app_commands.Choice(name="Single", value=2),
        #         app_commands.Choice(name="All", value=3),
        #     ]
        # )
        # async def repeat(self, interaction: Interaction, setting: app_commands.Choice[int]):
        #     await self.client.set_repeat(setting.value)
        #     await interaction.response.send_message(f"Now repeating: {setting.name}")

    @app_commands.command(description="Show the state of the queue.")
    async def show_queue(self, interaction: Interaction):
        msg = self.client.pretty_print_state()
        await interaction.response.send_message(msg)
