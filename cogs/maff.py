'''
Zeke Bot - Mental Math game cog, challenge your friends to a math game and display the current standings
Author: Zayn Ali Khan
Version Date: 6-9-2022
Email: zaynalikhan@gmail.com
Changes: 6-7(8)-2022 added interactive leaderboard (usability)
         6-8-2022 converted math to slash command (integrated with discord.py 2.0)
         6-16-2022 condensing code, removing modes for /math challenge for sake of clarity

'''
import re
import time
import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import database
import math

import miscellaneous


class MentalMath(commands.GroupCog, group_name="math"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot=bot
        self.running_commands=set() #temporary solution for preventing spam on the bot
                                   #if the current channel is running a game (id present in the set), wait until it is completed
        self.embed_pos=0 # the current page number being visited (scroll to leaderboard() for more detail)



    # check running_commands for a running game
    def prevent_spam(self, interaction: discord.Interaction) -> bool:
        if (interaction.channel_id in self.running_commands):
            return True
        return False

    # indicates a game is finished, a new cmd can be run
    def clear_cmd(self, interaction:discord.Interaction):
        self.running_commands.remove(interaction.channel_id)

    # initialize a user on the leaderboard if they are yet to be added
    def check_leaderboard(self, user_id, guild_id):
        if (not user_id in database.db[guild_id]['math_leaderboard'].keys()):
            database.db[guild_id]['math_leaderboard'].update({f'{user_id}':0})
            to_store=database.db[guild_id]['math_leaderboard']
            database.store_data(key='math_leaderboard',guild_id=guild_id, data=to_store)

    # Mental Math game that generates a random question within reasonable number range (+,-, or *), updating
    # the leaderboard with the user that has the most points
    @app_commands.command(name="challenge", description="Challenge a server member to a mental math duel, for mode specify 'mc' or 'writing'")
    async def challenge(self,interaction: discord.Interaction, user:str, rounds:int):
        print(user)
        if (user=="<@{}>".format(self.bot.user.id)): # don't challenge the bot
            await interaction.response.send_message("`Hey, you can't challenge me!`")
            return

        if self.prevent_spam(interaction): # dm the user if duplicate calls are detected
            await interaction.user.send("`{}, #{} is already running a game, please wait until it is finished`".format(interaction.user.name,interaction.channel.name))
            await interaction.response.send_message("\u200b")
            return
        else: self.running_commands.add(interaction.channel_id)
        server_id = interaction.guild_id
        rt=":white_check_mark:"
        wrong=":x:"
        praise=":congratulations:"

        # checking for valid input
        if (not user.startswith("<@")):
            await interaction.response.send_message("\n\n\n`Error: the correct format for this command is '!math challenge <@user> <#rounds> <gamemode: either 'mc' or 'writing'>'`")
            self.clear_cmd(interaction)
            return
        if (rounds>=25 or rounds<1):
            await interaction.response.send_message("\n\n`Invalid # of rounds (1-25 max)`")
            self.clear_cmd(interaction)
            return

        accept=['y', 'yes']
        decline=['n','no']
        mentioned_userid=int(re.search(pattern=r'\d+', string=user).group()) # save the challenged user's id, parsing the discord mention
        # if the parsed id is a guild member id, begin the match
        for member in self.bot.users:
            if (int(mentioned_userid)==int(member.id)):
                challenge_embed=discord.Embed(colour=discord.Colour.dark_red()).add_field(name="Alert...",value=("<@{}> `has challenged` <@{}> `to a Mental Math Duel!`".format(interaction.user.id,mentioned_userid) +
                                                       "\n\n*Do you accept?* (y/n)"))
                await interaction.response.send_message(embed=challenge_embed)
                def check(message):
                    return int(message.author.id)==int(mentioned_userid) and message.content.lower() in accept+decline
                try:
                    # listen for message, check if it is the challenged user (whether they accept the match or not)
                    # return value is the message that 'check' validates
                    # timeout if the user doesn't respond in time
                    msg=await self.bot.wait_for('message', timeout=30.0,check=check)
                except asyncio.TimeoutError:
                    await interaction.followup.send("`Challenge response not given in time`")
                    self.clear_cmd(interaction)
                    return
                else:
                    isAccepted = True if (msg.content.lower() in accept) else False
                    if (isAccepted):
                            # using dictionaries to store math operations
                            # a random index is generated in-range, and that is the math question to display
                            # 0 -> add
                            # 1 -> subtract
                            # 2 -> multiply
                            participant_ids={interaction.user.id:0,mentioned_userid:0}
                            operators={0:lambda x,y: x+y, 1: lambda x,y: x-y, 2: lambda x,y: x*y}
                            operator_str={0:'+',1:'-',2:'*'}
                            operation_range={0: 500, 1: 500, 2:50}
                            await interaction.channel.send("\n\n`Challenge Accepted!`")
                            time.sleep(1)
                            await interaction.channel.send("\n\n`Ready?`")
                            time.sleep(1)
                            await interaction.channel.send("\n`Steady?`")
                            time.sleep(1)
                            await interaction.channel.send("\n`Go!`")

                            for i in range(rounds): # each iteration generates a question, there are two options from here based on the mode
                                time.sleep(1)
                                operation_index=random.randint(0,2)
                                operand_one=random.randint(0,operation_range[operation_index])
                                operand_two=random.randint(0, operation_range[operation_index])
                                await interaction.channel.send(embed=discord.Embed(title="`Question {}.`".format(i+1),
                                                                           description="**`{}{}{}`**".format(operand_one,operator_str[operation_index],operand_two), colour=discord.Colour.dark_purple()))
                                answer=operators[operation_index](operand_one,operand_two)

                                # multiple-choice mode - generate several buttons with random values (close to the answer), one is the correct answer


                                # callback if the wrong button is pressed
                                # decrement user's score, continue to next iteration naturally
                                # taunt the user
                                async def fail(interaction:discord.Interaction):
                                    u=interaction.user.id
                                    if u in participant_ids.keys():
                                        await interaction.response.send_message("<@{}> `is Wrong! (-1)` {}".format(u,wrong))
                                        target=str(u)
                                        if (miscellaneous.taunts_available(guild_id=server_id,user_id=target)):
                                            size = len(database.db[server_id]['banter'][target])
                                            taunt = miscellaneous.generate_taunt(target=target, taunt=
                                            database.db[server_id]['banter'][target][random.randint(0, size-1)])
                                            await interaction.followup.send(taunt)

                                        participant_ids[u] = participant_ids[u] - 1
                                    else:
                                        await interaction.response.defer()

                                # callback for the single correct button
                                # increment user's score, continue to the next question by halting the current button-populated view
                                async def success(interaction:discord.Interaction):
                                    u=interaction.user.id
                                    if u in participant_ids.keys():
                                        await interaction.response.send_message("<@{}> `has scored a point! (+1)` {}".format(u,rt))
                                        participant_ids[u] = participant_ids[u] + 1
                                        view.stop()
                                    else:
                                        await interaction.response.defer()

                                buttons=[discord.ui.Button(label=f"{answer}",style=discord.ButtonStyle.blurple)]
                                buttons[0].callback=success
                                view = discord.ui.View(timeout=40) # users have 40 seconds to answer, or the match terminates, View houses the discord Buttons
                                for i in range(1,10):
                                    a=random.randint(answer-50,answer+50)
                                    while (a==answer):
                                        a=random.randint(answer-50,answer+50)
                                    buttons.append(discord.ui.Button(label=f"{a}",style=discord.ButtonStyle.blurple))
                                    buttons[i].callback=fail
                                random.shuffle(buttons) #shuffle button order (the correct one is instantiated first so it would be too easy otherwise)
                                for item in buttons:
                                    view.add_item(item)
                                await interaction.channel.send(view=view)
                                timeout=await view.wait()
                                if (timeout):
                                    await interaction.channel.send("\n\n`Correct answer not given in time, match terminated!`")
                                    self.clear_cmd(interaction)
                                    return

                            # update the winner based on the superior count stored in a dictionary of user ids
                            if (participant_ids[interaction.user.id] != participant_ids[mentioned_userid]):
                                winner = interaction.user.id if participant_ids[interaction.user.id] > participant_ids[
                                    mentioned_userid] else mentioned_userid
                                await interaction.channel.send("\n\n`The winner is` <@{}> `with a score of {}!` {}".format(winner,participant_ids[winner],praise))

                                # increment the win-count of the user in the server database

                                database.add_instance(server_id)
                                self.check_leaderboard(str(interaction.user.id),server_id)
                                self.check_leaderboard(str(mentioned_userid),server_id)
                                copy=database.db[server_id]['math_leaderboard']
                                copy[f'{winner}']=copy[f'{winner}']+1
                                database.store_data(key='math_leaderboard',guild_id=server_id,data=copy)
                                self.clear_cmd(interaction)
                                return
                            else:
                                await interaction.channel.send("\n\n`We have a tie! None of y'all get jack`")
                                self.clear_cmd(interaction)
                                return

                    else:
                        # if a user has declined the match, taunt them!
                        await interaction.channel.send("<@{}> `has declined the challenge!`".format(mentioned_userid))

                        if (miscellaneous.taunts_available(guild_id=server_id, user_id=mentioned_userid)):
                            size = len(database.db[server_id]['banter'][mentioned_userid])
                            taunt = miscellaneous.generate_taunt(target=mentioned_userid, taunt=database.db[server_id]['banter'][mentioned_userid][random.randint(0, size-1)])
                            await interaction.followup.send(taunt)
                        self.clear_cmd(interaction)
                        return

        # the loop doesn't find the user
        await interaction.channel.send("`User does not exist, please specify someone present in the server!`")
        self.clear_cmd(interaction)

    # interactive leaderboard storing each member's win-count
    @app_commands.command(name="leaderboard", description="Display match statistics for Mental Math Challenge (currently top 3 in the server")
    async def leaderboard(self, interaction:discord.Interaction):

        server_id=interaction.guild_id
        database.add_instance(server_id) # initialize server database if needed

        # check if the leaderboard is empty
        ref=len(database.db[server_id]['math_leaderboard'].keys())
        if (ref==0):
            await interaction.response.send_message("`Leaderboard is empty (not initialized), play a game to update it`")
            return

        # construct leaderboard
        raw_stats=database.db[server_id]['math_leaderboard'] # order is {user: win-count}

        # sort the original dictionary by most prevalent win-count, since dictionaries are unsorted, we need to do some
        # re-arranging of the key-list order
        conversion={}
        for k in raw_stats:
            conversion[k]=int(raw_stats[k])
        conversion=dict(sorted(conversion.items(), key=lambda item: item[1],reverse=True))

        # generate the leaderboard pages, storing each user stat as an embed field fitted on the page
        count=0
        identifier=[':first_place:',':second_place:',':third_place:']
        element_num=0
        pages = int(math.ceil(ref/5)) # determine the number of pages, rounded to the nearest whole that is >= to # users
        embeds=[]
        page_num=0

        # initalize the necessary pages
        for i in range(pages):
            embeds.append(discord.Embed(title="`Math Leaderboard <Wins>`", colour=discord.Colour.dark_gold()).set_footer(text="Page {}/{}".format(i+1, pages)))

        # add the user information to a page, if the number of items in a page exceeds 5, use the next page
        for item in conversion:
            if (count + 1 <= 3): # just an aesthetic thing, identifier stores emojis
                place = identifier[count]
            else:
                place=str(count+1) + "."
            member = self.bot.get_user(int(item))
            embeds[page_num].add_field(name=f'\n {place} `{member.name}#{member.discriminator} - {conversion[item]}`', value="\u200b",inline=False)
            count=count+1
            element_num=element_num+1
            if (element_num==5): # if the current page cycle has 5 items, reset the count and allocate another page
                element_num=0
                page_num=page_num+1

        # move back a page if Back button is pressed (if applicable)
        async def back(interaction:discord.Interaction):
            if (self.embed_pos-1>=0):
                self.embed_pos=self.embed_pos-1
                await leaderboard.edit(embed=embeds[self.embed_pos])
            await interaction.response.defer()

        # move up a page if Next button is pressed (if applicable)
        async def next(interaction: discord.Interaction):
            if (self.embed_pos+1<len(embeds)):
                self.embed_pos=self.embed_pos+1
                await leaderboard.edit(embed=embeds[self.embed_pos])
            await interaction.response.defer()

        # exit the leaderboard
        async def exit(interaction: discord.Interaction):
            await interaction.response.send_message("`Closing Leaderboard...`")
            view.stop()
            await leaderboard.delete()


        view = discord.ui.View(timeout=120)
        back_button=discord.ui.Button(label="Back",style=discord.ButtonStyle.gray)
        next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.gray)
        delete = discord.ui.Button(label='Exit', style=discord.ButtonStyle.danger)
        view.add_item(back_button)
        view.add_item(next_button)
        view.add_item(delete)
        await interaction.response.send_message(embed=embeds[0],view=view)
        leaderboard=await interaction.original_message()
        back_button.callback=back
        next_button.callback=next
        delete.callback=exit
        timeout=await view.wait()

        if (timeout):
            await interaction.followup.send("`Closing Leaderboard...`")
            view.stop()
            await leaderboard.delete()
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(MentalMath(bot))
