'''
Zeke Bot - Class for miscellaneous tasks such as checking for the existence of data in the server document
or initializing data for the functionality of specific cogs if missing
Author: Zayn Khan
Version Date: 6-12-2022
Email: zaynalikhan@gmail.com

'''
import discord

import database
import validators

'''
This section pertains to banter.py checks
'''

# a random index will be generated in a list of taunts directed
# at a specified user, so we must check if the list is empty first
def taunts_available(guild_id, user_id) -> bool:
    initialize_banters(guild_id=guild_id,user_id=user_id)
    return False if len(database.db[guild_id]['banter'][user_id])==0 else True

# initialize the user key in the database if not yet added
def initialize_banters(guild_id, user_id):
    database.add_instance(guild_id)
    if str(user_id) not in database.db[guild_id]['banter'].keys():
        database.db[guild_id]['banter'].update({f'{user_id}': []})
        to_store = database.db[guild_id]['banter']
        database.store_data(key='banter',guild_id=guild_id,data=to_store)

# generate a taunt message to be sent by any command
def generate_taunt(target: str, taunt: str):
    if (validators.url(taunt)):
        return f'<@{target}>: {taunt}'
    else:
        return f'<@{target}>: `{taunt}`'


# Overwritten discord view for ease of access in cogs
class Interact(discord.ui.View):
    def __init__(self, num_pages, embeds: [discord.Embed], timeout):
        super().__init__()
        self.pages=num_pages
        # the search results will usually have multiple pages, and we want to update the message with
        # a discord embed at a new given index in the array depending on if they hit back or next
        self.embed_pos=0
        self.embeds=embeds
        self.timeout=timeout


    async def on_timeout(self):
            await self.message.delete()
            self.stop()

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.embed_pos - 1 >= 0): # move back a page, if applicable
            self.embed_pos = self.embed_pos - 1
            await self.message.edit(embed=self.embeds[self.embed_pos])
        await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.embed_pos + 1 < self.pages): # move up a page, if applicable
            self.embed_pos = self.embed_pos + 1
            await self.message.edit(embed=self.embeds[self.embed_pos])
        await interaction.response.defer()

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("`Exiting search...`")
        await self.message.delete()
        self.stop()
