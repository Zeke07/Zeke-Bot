'''
Zeke Bot - Banter cog for generating taunts directed at specific users
Author: Zayn Khan
Version Date: 6-12-2022
Email: zaynalikhan@gmail.com
'''
import discord
from discord.ext import commands
from discord import app_commands
import database
import miscellaneous


class Banter(commands.GroupCog, group_name="banter"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot=bot


    # /banter add 
    # add a taunt directed at a specific user to the server database
    @app_commands.command(name="add", description="add text taunts")
    async def add(self, interaction:discord.Interaction, target_user: str, taunt: str):
        ''' code structure for sending banter (just an aesthetic thing)
        taunt=self.generate_taunt(target=target,taunt=taunt)
        if type(taunt)==discord.Embed:
            await interaction.response.send_message(embed=taunt)
        else:
            await interaction.response.send_message(taunt)
        '''

        if (not target_user.startswith("<@")):
            await interaction.response.send_message('`Target user must have an @`')
            return
        if (len(taunt)>4096):
            await interaction.response.send_message('`Taunt is too long (longer than 4096 characters) or be a url`')

        server_id=interaction.guild_id
        mem_id=target_user[3:len(target_user)-1]
        miscellaneous.initialize_banters(server_id, mem_id)

        # add taunt to list in database keyed by user's id
        # the DB 'banter' key in the document stores keys of user_ids, each referring to
        # a list full of taunts directed at that specific user
        database.add_instance(server_id)
        database.db[server_id]['banter'][mem_id].append(taunt)
        to_store=database.db[server_id]['banter']
        database.store_data(key='banter',guild_id=server_id,data=to_store)

        await interaction.response.send_message(f'`Updated banter for` {target_user}')



async def setup(bot: commands.Bot):
    await bot.add_cog(Banter(bot))
