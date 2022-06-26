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
import random
from miscellaneous import Interact
class Banter(commands.GroupCog, group_name="banter"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot=bot

    
    @app_commands.command(name="say", description="utter a taunt")
    async def say(self, interaction:discord.Interaction, target_user:str):
        if (not target_user.startswith("<@")):
            await interaction.response.send_message('`Target user must have an @`')
            return
        mentioned_userid = target_user[3:len(target_user) - 1]
        server_id=interaction.guild_id
        if (miscellaneous.taunts_available(guild_id=server_id, user_id=mentioned_userid)):
            size = len(database.db[server_id]['banter'][mentioned_userid])
            taunt = miscellaneous.generate_taunt(target=mentioned_userid,
                                                 taunt=database.db[server_id]['banter'][mentioned_userid][
                                                     random.randint(0, size - 1)])
            await interaction.response.send_message(taunt)
            return
        else:
            await interaction.response.send_message("`No taunts available for this user, use '/banter add' to create one`")
            return
    # /banter add
    # add a taunt directed at a specific user to the server database
    @app_commands.command(name="add", description="add text taunts")
    async def add(self, interaction:discord.Interaction, target_user: str, taunt:str):
        if (not target_user.startswith("<@")):
            await interaction.response.send_message('`Target user must have an @`')
            return
        if (len(taunt)>4096):
            await interaction.response.send_message('`Taunt is too long (longer than 4096 characters)`')

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
        
    # INCOMPLETE, selection menu soon to be added to properly implement removal function
    # /banter remove
    # display or remove taunts for a specific user
    @app_commands.command(name="remove", description="add text taunts")
    async def remove(self, interaction: discord.Interaction, target_user: str):
        if (not target_user.startswith("<@")):
            await interaction.response.send_message('`Target user must have an @`')
            return

        server_id = interaction.guild_id
        mem_id = target_user[3:len(target_user) - 1]
        print(mem_id)
        banter=database.db[server_id]['banter']
        if not mem_id in banter.keys():
            await interaction.response.send_message("`Target user has no taunts to display, use '/banter add' to create one`")
            return

        member = self.bot.get_user(int(mem_id))
        to_display=banter[mem_id]
        embeds=[]
        descriptions=[""]
        index=0
        count=1
        single_page=True
        for taunt in to_display:
            if (len(descriptions[index]+taunt)<=4096):
                descriptions[index]+=f'\n`{count}. {taunt}`'
                count+=1
            else:
                descriptions.append("")
                index+=1
                descriptions[index]+=f'\n`{count}. {taunt}`'
                count+=1
        pages=len(descriptions)
        count=1
        for desc in descriptions:
            embeds.append(discord.Embed(title=f"`Banter for {member.name}#{member.discriminator}`", description=desc, colour=discord.Colour.dark_orange()).set_footer(text=f'Page {count}/{pages}'))
            count+=1
       
        #await interaction.response.send_message(embed=embeds[0])
        #await interaction.followup.send(embed=embeds[1])

        '''
                   description=""
                   if (len(taunt+description)<=5):
                       description+=f'\n`{count}. {taunt}`'
                       count+=1
                   else:
                       single_page=False
                       embeds.append(discord.Embed(title=f"`Banter for {member.name}#{member.discriminator}`", description=description))
                       description=""

               if single_page:
                   embeds.append(discord.Embed(title=f"`Banter for {member.name}#{member.discriminator}`", description=description))
        '''




async def setup(bot: commands.Bot):
    await bot.add_cog(Banter(bot))
