'''
Zeke Bot - Class for miscellaneous tasks such as checking for the existence of data in the server document
or initializing data for the functionality of specific cogs if missing
Author: Zayn Khan
Version Date: 6-16-2022
Email: zaynalikhan@gmail.com

'''
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
