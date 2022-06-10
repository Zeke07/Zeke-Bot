'''
Zeke Bot - Database, using a MongoDB collection
Author: Zayn Ali Khan
Email: zaynalikhan@gmail.com
'''
from pymongo import MongoClient
from dotenv import dotenv_values

env_vars=dotenv_values()
client=MongoClient(env_vars['DB_CONNECT'])
collection=client['zeke_bot']['zeke_database']
db=dict()

INSTANCE_DATA= {
        'server_id': 0,
         'math_leaderboard': {},
        'banter': []

}

# load each document (representing a server's data)
# as a value in a dictionary variable, the key being
# the server's unique id as a discriminator
for docs in collection.find({}):
    db[docs['server_id']]=docs

# initialize a new document for a given server
def add_instance(guild_id):
    if not guild_id in db.keys():
        INSTANCE_DATA.update({'server_id':guild_id})
        collection.insert_one(INSTANCE_DATA)
        db[guild_id]=INSTANCE_DATA
        print("Created database entry for the following server id: {}".format(guild_id))

# replace the value of a certain key within the server data dictionary
# ex: if I want to change the win-rate of one user, create a temp variable storing the current
# leaderboard dictionary, add to it, then call this method with temp as the data (see /math challenge for more insight)
def store_data(key, guild_id, data):
    try:
        print(f'Updating {key} with {data}')
        db[guild_id][key]=data
        collection.update_one({'server_id': guild_id}, {"$set": {key: data}})
    except Exception:
        raise ConnectionError("Cannot connect to database")

# remove a document, if my Cloud DB is populated enough, I'll add an event listener in main
# to remove a server document if the bot is removed (kicked/banned/etc)
def remove_data(guild_id):
    collection.delete_one({'server_id':guild_id})
    db[guild_id].clear()
