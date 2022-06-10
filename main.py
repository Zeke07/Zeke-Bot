'''
Driver for Zeke Bot, Python/Discord.py 2.0
Author: Zayn Khan
Email: zaynalikhan@gmail.com

'''

import discord
import os
from dotenv import dotenv_values
from discord.ext import commands

dict=dotenv_values()# load environment vars into dictionary (key-value pairs) from the .env in this directory

# synonymous with discord.Client
class Zeke(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!',intents=discord.Intents.all(),
                       application_id=dict['APP_ID']) # application_id must be specified for sync() call
                                                      # prefix is unused now that slash commands are added

    #runs when the bot has undergone its launch procedures [let's me know that it is functional in 'x' list of servers]
    async def on_ready(self):
        guild_titles = []
        for n in self.guilds:
            guild_titles.append(n.name)
        print('We have logged in as {0.user} to the following guilds: {1}'.format(self, guild_titles))

    #overwritten discord method, ties to the setup() method in each cog
    #find /cog folder in this directory and load all class files
    async def setup_hook(self):
        for file in os.listdir("cogs/"):
            if (file.endswith(".py")):
                await self.load_extension("cogs.{}".format(file[:-3]))

        await zeke_client.tree.sync() # sync slash commands globally

    #not entirely necessary yet, but will be once I host the bot in a vm
    async def close(self):
        await super().close()


zeke_client=Zeke()
zeke_client.run(dict['DISCORD_KEY']) # launch bot with hidden key
