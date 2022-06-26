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
class Banter(commands.GroupCog, group_name="banter"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot=bot

    # /banter say
    # utter a random taunt from a user's cache
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
        if taunt in database.db[server_id]['banter'][mem_id]:
            await interaction.response.send_message(f'`Taunt already exists!`')
            return
        if (len(database.db[server_id]['banter'][mem_id])<25):
            database.db[server_id]['banter'][mem_id].append(taunt)
            to_store=database.db[server_id]['banter']
            database.store_data(key='banter',guild_id=server_id,data=to_store)
            await interaction.response.send_message(f'`Updated banter for` {target_user}')
        else:
            await interaction.response.send_message(f'`Failed: maximum capacity of taunts for each user is 25`')




    # /banter remove
    # display or remove taunts for a specific user
    @app_commands.command(name="remove", description="add text taunts")
    async def remove(self, interaction: discord.Interaction, target_user: str):
        if (not target_user.startswith("<@")):
            await interaction.response.send_message('`Target user must have an @`')
            return

        # always initialize mongodb before checking contents
        server_id = interaction.guild_id
        database.add_instance(server_id)
        mem_id = target_user[3:len(target_user) - 1]
        miscellaneous.initialize_banters(server_id, mem_id)
        banter = database.db[server_id]['banter']
        
        # no taunts to display
        if len(banter[mem_id])==0:
            await interaction.response.send_message("`Target user has no taunts to display, use '/banter add' to create one`")
            return

        # fetch taunts, initialize embed descriptions for each page (cannot exceed 4096 when the next taunt is concatenated)
        member = self.bot.get_user(int(mem_id))
        to_display=banter[mem_id]
        embeds=[]
        descriptions=[""]
        index=0
        count=1
        options=dict()
        for taunt in to_display:
            if (len(descriptions[index]+taunt)<=4096):
                descriptions[index]+=f'\n`{count}.` {taunt}'
                options[count]=taunt
                count+=1
            else:
                descriptions.append("")
                index+=1
                descriptions[index]+=f'\n`{count}.` {taunt}'
                options[count]=taunt
                count+=1
        pages=len(descriptions)
        count=1
        
        # each description string in the array represents a page, intialize them
        for desc in descriptions:
            embeds.append(discord.Embed(title=f"`Banter for {member.name}#{member.discriminator}`", description=desc, colour=discord.Colour.dark_orange()).set_footer(text=f'Page {count}/{pages}'))
            count+=1

        # callback for the select menu
        # each time a number is selected, the item is deleted and the menu is refreshed
        async def upon_select(interaction:discord.Interaction):
            to_remove=interaction.data['values'][0]
            database.db[server_id]['banter'][mem_id].remove(to_remove)
            curr_options=select_menu.options
            for opt in curr_options:
                if opt.value==to_remove:
                    curr_options.remove(opt)
            view.remove_item(select_menu)
            select_menu.options=curr_options
            view.add_item(select_menu)
            to_store=database.db[server_id]['banter']
            database.store_data(key='banter', guild_id=server_id, data=to_store)
            if (len(curr_options)<1):
                await interaction.response.send_message("`Taunt deleted, session ended`")
                await view.message.delete()
                view.stop()

            else:
                await view.message.edit(view=view)
                await interaction.response.send_message("`Taunt deleted`")

        # create view display with interactive menu, listen for interactions
        view=miscellaneous.Interact(num_pages=len(embeds),embeds=embeds, timeout=60)
        select_menu=discord.ui.Select(placeholder="Select taunt # (Removed upon selection)")

        for item in options.keys():
            select_menu.add_option(label=item,value=options[item])

        view.add_item(select_menu)
        select_menu.callback=upon_select
        await interaction.response.send_message(embed=embeds[0],view=view)
        view.message = await interaction.original_message()





async def setup(bot: commands.Bot):
    await bot.add_cog(Banter(bot))
