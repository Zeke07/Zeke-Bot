'''
Zeke Bot - Henle cog, query henle.de for a specified search key
Author: Zayn Khan
Version Date: 6-10-2022
Email: zaynalikhan@gmail.com
Changes: bug fixes to scraper, interactive embeds

'''
import discord
from discord.ext import commands
from discord import app_commands

from bs4 import BeautifulSoup
import requests
import math
import asyncio

class Henle(commands.GroupCog, group_name="henle"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot=bot
        self.url="https://www.henle.de"
        self.item_query={} # important for usability, the user can simply input a number and it will fetch that item
        self.num_results=0 # the # of search results

    # helper for generating embed pages containing the search results
    # follows a similar procedure to generating the leaderboard (see /math leaderboard)
    def generate_page(self, queries: dict) -> [discord.Embed]:

        pages = int(math.ceil(len(queries.keys())/ 5))
        embeds=[]
        for i in range(pages):
            embeds.append(discord.Embed(title="`Henle Search Results`", colour=discord.Colour.blue(),description="").set_footer(text="Page {}/{}".format(i+1, pages)).set_thumbnail(url="https://play-lh.googleusercontent.com/Wiaz0BsQDxl51R5i7kYrkS9TWIGInaXzQh8mnVlhissCSkYqGRejkspNQ7_xGpyvJ0U"))
        description = str()
        count = 1
        element_num = 0
        page_num = 0
        for item in queries.keys():
            embeds[page_num].add_field(name=f'\n`{count}. {item}`',
                        value="\u200b", inline=False)
            self.item_query[count]=item
            count = count + 1
            element_num = element_num + 1
            if (element_num == 5):
                element_num = 0
                page_num = page_num + 1
        self.num_results=len(queries.keys())
        return embeds

    # Search for any musical piece present on henle.de
    # Make an initial query, then choose from a list of fetched results to retrieve the contents
    @app_commands.command(name="search", description="Search Henle for any musical piece")
    async def henle_search(self, interaction:discord.Interaction, query:str):

        # fetch the search engine url and send out a request
        # with a link containing the attached user query
        url = "https://www.henle.de/us/search/?q=" + str(query)

        url_request = requests.get(url)

        # parse the search-result webpage
        content = BeautifulSoup(url_request.text, "html.parser")
        search_results = content.find_all("article", {"class": "result-item clearfix"})

        result_dictionary = dict() # will store each result title as a key, the value being a url to the contents
        if (len(search_results) < 1):
            await interaction.response.send_message(f'`No results found!`')
            return
        for i in search_results:
            key = i.find("h2", {"class": "sub-title"}).string + " - " + i.find("h2", {"class": "main-title"}).string
            href = i.find("a", {"class": "cover-wrapper"})['href']
            result_dictionary[key] = "https://www.henle.de" + href

        # show the search results
        # when generate page is called, the instance's item_query dictionary will store the title key of piece (used to fetch the hyperlink-
        # from the result_dictionary) as a value assigned with a number-key that the user will input to choose the content they want
        embeds=self.generate_page(queries=result_dictionary)
        view=Interact(num_pages=len(embeds),embeds=embeds,timeout=60) # the view is an Interact instance set inside the message below
        await interaction.response.send_message(embed=embeds[0], view=view)
        view.message = await interaction.original_message() # store the above message so it can be deleted upon exit/timeout
        await interaction.followup.send(f'`Found {self.num_results} results! Send the number of the piece you want to query`')

        # check for a number from the cmd user, if valid,
        # grab the composition name associated with that number
        def check(message):
            digit=message.content
            if (not message.content.isdigit()):
                return False
            return message.author.id==interaction.user.id and int(digit) in self.item_query.keys()
        try:
            # listen for message, check if it is the command author
            # return value is the message that 'check' validates
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            # terminate if the user doesn't respond
            self.item_query = {}
            self.num_results = 0
            await interaction.followup.send("`Response not given in time`")
            return

        redirect=int(msg.content)
        composition_title = self.item_query[redirect] # embed title, but also used to grab the hyperlink

        # send a final request to the webserver about the content the user wants
        # parse it for key information such as the piece names (if the chosen composition is a set of pieces), difficulty,
        # description, etc
        fetch_url=result_dictionary[composition_title]
        final_request= requests.get(fetch_url)
        final_content=BeautifulSoup(final_request.text, "html.parser")
        desc_node= final_content.find('div', {"class": "article-text"})
        composition_description=""
        if desc_node is not None:
            composition_description=desc_node.find("p").contents[0]
        compositions=final_content.find_all('ul', {"class": "content-item"})
        piece_stats=[]
        for item in compositions:
            if ("headline" in str(item)):
                continue

            content_title=item.find('li', {"class": "column-title"})
            if (content_title is not None):
                content_title=content_title.string
            else:
                content_title=""
            grade=item.find('span', {"class": "grade-circle"})
            if (grade is not None):
                grade=grade.string
            else:
                grade=" "
            instrument=str(item.find('li', {"class": "column-difficulty"}).contents[0]).strip()
            piece_stats.append(f'{content_title} - Difficulty: {grade}/9 ({instrument})')

        # display the parsed information in a single embed that links to the henle page
        # terminate after the user hits exit, or if the embed times out
        final_view=Interact(num_pages=0,embeds=[],timeout=120)
        c=1
        description=f'`Description: \n{composition_description}`'
        for elem in piece_stats:
            if (len(description+elem) <= 4096):
                description+= '\n\n' + f'`{c}. {elem}`'
                c=c+1
            else:
                break
        final_view.message=await interaction.followup.send(embed=discord.Embed(title=composition_title,description=description,colour=discord.Colour.dark_red(),url=fetch_url).set_thumbnail(url="https://play-lh.googleusercontent.com/Wiaz0BsQDxl51R5i7kYrkS9TWIGInaXzQh8mnVlhissCSkYqGRejkspNQ7_xGpyvJ0U"), view=final_view)

        self.item_query = {}
        self.num_results = 0
        return





# Overwritten discord view for ease of access
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
        if (self.embed_pos + 1 <= self.pages): # move up a page, if applicable
            self.embed_pos = self.embed_pos + 1
            await self.message.edit(embed=self.embeds[self.embed_pos])
        await interaction.response.defer()

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("`Exiting search...`")
        await self.message.delete()
        self.stop()


async def setup(bot: commands.Bot):
    await bot.add_cog(Henle(bot))