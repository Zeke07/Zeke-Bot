'''
Work-in-progress
(i.e. did not get to it yet because I really wanted to write /henle)

'''
import discord
from discord.ext import commands
from discord import app_commands


class Banter(commands.GroupCog, group_name="banter"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot=bot

    @app_commands.command(name="add", description="add text taunts")
    async def add(self, interaction:discord.Interaction):
        await interaction.response.send_message("hi")


async def setup(bot: commands.Bot):
    await bot.add_cog(Banter(bot))