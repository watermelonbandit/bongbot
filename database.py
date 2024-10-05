import pymongo
import asyncio
from mongo_database_connection import get_database
from bson import ObjectId

bongbotdatabase = get_database()


async def server_setup(guild_id, bongbot_channelid, lowest_role_id, bongbot_goldenbong, time_keeper_role, admin_role, bong_bot_time):
    discord_server_database = bongbotdatabase[f'{guild_id}']
    # Check if the settings document exists for the given guild
    existing_settings = await discord_server_database.find_one({"_id": guild_id})
    
    if existing_settings:
        update_fields = {}
        if bongbot_channelid is not None:
            update_fields["settings.bongbot_channelid"] = bongbot_channelid
        if bongbot_goldenbong is not None:
            update_fields["settings.bongbot_goldenbong"] = bongbot_goldenbong
        if lowest_role_id is not None:
            update_fields["settings.lowest_role"] = lowest_role_id
        if time_keeper_role is not None:
            update_fields["settings.timekeeper_role_id"] = time_keeper_role
        if admin_role is not None:
            update_fields["settings.admin_role_id"] = admin_role
        if bong_bot_time is not None:
            update_fields["settings.bong_bot_time"] = bong_bot_time

        if update_fields:
            update_settings = {
                "$set": update_fields
            }
            await discord_server_database.update_one({"_id": guild_id}, update_settings, upsert=True)
    
    else:
        # Insert new settings
        settings = {
            "_id": guild_id,
            "settings": {
                "bongbot_channelid": bongbot_channelid,
                "bongbot_goldenbong": bongbot_goldenbong,
                "lowest_role": lowest_role_id,
                "timekeeper_role_id": time_keeper_role,
                "admin_role_id": admin_role,
                "bong_bot_time": bong_bot_time,
                "guild_id": guild_id
            }
        }
        await discord_server_database.insert_one(settings)
    
    print("database updated")




async def dynamic_resource(guild_id, golden_bong_timestamp, sc_channel, member):
    discord_server_database = bongbotdatabase[f'{guild_id}']
    # Check if the settings document exists for the given guild
    existing_dynamics = await discord_server_database.find_one({"_id": guild_id})
    

    if existing_dynamics:
        update_fields = {}
        if golden_bong_timestamp is not None:
            update_fields["dynamics.golden_bong_timestamp"] = golden_bong_timestamp
        if sc_channel is not None:
            update_fields["dynamics.sc_channel"] = sc_channel
        if member is not None:
            update_fields["dynamics.golden_bong_winner"] = str(member)

        if update_fields:
            update_dynamics = {
                "$set": update_fields
            }
            await discord_server_database.update_one({"_id": guild_id}, update_dynamics, upsert=True)
    else:
        # Insert new settings
        golden_bong_info = {
            "_id": guild_id,
            "settings": {
                "golden_bong_timestamp": golden_bong_timestamp,
                "sc_channel": sc_channel,
                "golden_bong_winner": member
            }
        }   
        await discord_server_database.insert_one(golden_bong_info)
    
    print("database updated")

async def streak(guild_id, streak):
    discord_server_database = bongbotdatabase[f'{guild_id}']
    existing_streak = await discord_server_database.find_one({"_id": guild_id})
    

    if existing_streak:
        update_fields = {}
        if streak is not None:
            update_fields["dynamics.streak"] = streak

        if update_fields:
            update_settings = {
                "$set": update_fields
            }
            await discord_server_database.update_one({"_id": guild_id}, update_settings, upsert=True)
    else:
        streak  = {
            "_id": guild_id,
            "dynamics": {
                "streak": streak
            }
        }
        await discord_server_database.insert_one(streak)


async def points(guild_id, points):
    discord_server_database = bongbotdatabase[f'{guild_id}']
    existing_streak = await discord_server_database.find_one({"_id": guild_id})
    
    if existing_streak:
        update_fields = {}
        if streak is not None:
            update_fields["dynamics.points"] = streak

        if update_fields:
            update_settings = {
                "$set": update_fields
            }
            await discord_server_database.update_one({"_id": guild_id}, update_settings, upsert=True)
    else:
        point  = {
            "_id": guild_id,
            "dynamics": {
                "points": points
            }
        }
        await discord_server_database.insert_one(point)
    

async def get_server_data(guild_id):
    
    discord_server_database = bongbotdatabase[f'{guild_id}']

    cursor = discord_server_database.find()

    user_bong_data_dict = {}

    async for document in cursor:
        user_bong_data = document.get("user_bong_data", {})
        
        for member_id, data in user_bong_data.items():
            user_bong_data_dict[member_id] = {
                "bongs": data.get("bongs"),
                "reaction_time": data.get("reaction_time"),
                "golden_bongs": data.get("golden_bongs"),
                "time_69_bongs": data.get("time_69_bongs")
            }

            if user_bong_data_dict[member_id]['time_69_bongs']:
                print(user_bong_data_dict[member_id]['time_69_bongs'])
    
    
    return user_bong_data_dict


async def get_server_blacklist(guild_id):
    discord_server_database = bongbotdatabase[f'{guild_id}']

    cursor = discord_server_database.find()

    server_blacklist = {}

    async for  document in cursor:
        members_blacklisted = document.get('blacklist', {})
        
        for member_id, data in members_blacklisted.items():
            server_blacklist[member_id] = {
                "reason": data.get("reason")
            }


    return server_blacklist



async def update_server_blacklist(guild_id, blacklist):
    # Access the specific guild collection
    discord_server_database = bongbotdatabase[f'{guild_id}']

    # Query to find the document where the specific member_id exists within user_bong_data
    
    await discord_server_database.update_one(
            {}, 
            {"$set": {"blacklist": blacklist}}, 
            upsert=True
        )


async def server_goldenbong_channellist(guild_id, channellist):
    discord_server_database = bongbotdatabase[f'{guild_id}']

    # Query to find the document where the specific member_id exists within user_bong_data
    
    await discord_server_database.update_one(
            {}, 
            {"$set": {"gb_channel_list": channellist}}, 
            upsert=True
        )


async def return_goldenbong_channelist(guild_id):
    
    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'gb_channel_list': 1})
    
    if document and 'gb_channel_list' in document:
        channel_list = document['gb_channel_list']
        print("1")
        print(channel_list)
        print("2")
        return channel_list
    else:
        return "Not here"
 
async def update_server_users(guild_id, leaderboard):
    # Access the specific guild collection
    discord_server_database = bongbotdatabase[f'{guild_id}']

    # Query to find the document where the specific member_id exists within user_bong_data
    
    await discord_server_database.update_one(
            {}, 
            {"$set": {"user_bong_data": leaderboard}}, 
            upsert=True
        )

async def get_points(guild_id):
    
    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'dynamics.points': 1})
    
    print(document)

    print("we got here")
    
    try: 
        if document or document != {} or document['dynamics'] != {}:
            points = document['dynamics']['points']
        else:
            points = 0
    except:
        points = 0
    
    print("this is the point value coming up right now, get ready")
    print(points)
    
    return points


async def update_server_points(guild_id, points):
    discord_server_database = bongbotdatabase[f'{guild_id}']
        
    await discord_server_database.update_one(
                {}, 
                {"$set": {"dynamics.points": points}}, 
                upsert=True
            )


async def override_server_Users(guild_id, member_id, hasBeenOveridden, new_bong_count):

    discord_server_database = bongbotdatabase[f'{guild_id}']
    existing_records = await discord_server_database.find_one({
        f"user_bong_data.{member_id}": {"$exists": True}
    })
    
    if existing_records:
        update_records = {
            "$set" : {
                f"user_bong_data.{str(member_id)}.bongs": f"{new_bong_count}",
                f"user_bong_data.{str(member_id)}.hasBeenOverriden": f"{hasBeenOveridden}"
            }
        }

        await discord_server_database.update_one({"_id": existing_records["_id"]}, update_records)
    
    else:
        user_bong_data = {
            "user_bong_data": {
                    f"{member_id}" : {
                        "hasBeenOverriden":f"{hasBeenOveridden}",
                        "bongs": f"{new_bong_count}"
                    }
            }
        }

        await discord_server_database.insert_one(user_bong_data)


async def get_channel(guild_id):
    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'settings.bongbot_channelid': 1})
    
    if document and 'settings' in document and 'bongbot_channelid' in document['settings']:
        bong_channel = document['settings']['bongbot_channelid']
        return int(bong_channel)
    else:
        return "Not here"

async def get_golden_bong_info(guild_id):
    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'dynamics': 1})
    
    if document and 'dynamics' in document and 'golden_bong_timestamp' in document['dynamics'] and 'sc_channel' in document['dynamics']:
        sc_channel_id = document['dynamics']['sc_channel']
        golden_bong_timestamp = document['dynamics']['golden_bong_timestamp']
        golden_bong_winner = document['dynamics']['golden_bong_winner']

        return sc_channel_id, golden_bong_timestamp, golden_bong_winner
    else:
        return "Not here"


async def get_time_keeper_role(guild_id):

    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'settings.timekeeper_role_id': 1})
    
    if document and 'settings' in document and 'timekeeper_role_id' in document['settings']:
        time_keeper_role_id = document['settings']['timekeeper_role_id']
        return int(time_keeper_role_id)
    else:
        return "Not here"

async def get_lowest_role(guild_id):
    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'settings.lowest_role': 1})
    
    if document and 'settings' in document and 'lowest_role' in document['settings']:
        lowestrole = document['settings']['lowest_role']
        return int(lowestrole)
    else:
        return "Not here"

async def get_admin_role(guild_id):
    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'settings.admin_role_id': 1})
    
    if document and 'settings' in document and 'admin_role_id' in document['settings']:
        adminrole = document['settings']['admin_role_id']
        return int(adminrole)
    else:
        return "Not here"

async def get_streak(guild_id):
    discord_server_database = bongbotdatabase[f'{guild_id}']

    document = await discord_server_database.find_one({}, {'_id': 0, 'dynamics.streak': 1})
    
    if document and 'dynamics' in document and 'streak' in document['dynamics']:
        streak = document['dynamics']['streak']
        return streak
    else:
        return "Not here"
    
async def get_global_points():
    points_dict = {}

    collections = await bongbotdatabase.list_collection_names()

    for guild in collections:
        collection = bongbotdatabase[guild]

        document = await collection.find_one()
        
        if document and 'dynamics' in document and 'points' in document['dynamics']:
            points = document['dynamics']['points']
            points_dict[guild] = points
            print(f"Collection: {guild}, Points: {points}")
        
    print(points_dict)
    return points_dict

async def get_bong_channel_id(guild_id):
    
    discord_server_database = bongbotdatabase[f'{guild_id}']
    document = await discord_server_database.find_one({}, {'_id': 0, 'settings.bongbot_channelid': 1})

    bong_bot_channel = document['settings']['bongbot_channelid']

    return int(bong_bot_channel)

async def get_bong_time(guild_id):
    discord_server_database = bongbotdatabase[f'{guild_id}']
    document = await discord_server_database.find_one({}, {'_id': 0, 'settings.bong_bot_time': 1})
    bong_bot_time = document['settings']['bong_bot_time']

    return bong_bot_time

async def get_server_ids():


    server_ids = await bongbotdatabase.list_collection_names()

    return server_ids

async def move_user_bong_data(interaction, season):


    server_ids = await bongbotdatabase.list_collection_names()
    
    for guild_id in server_ids:
        discord_server_database = bongbotdatabase[f'{guild_id}']
        print("1")
        
        document = await discord_server_database.find_one({"guild_id": guild_id})
        
        old_bong_data = await get_server_data(guild_id)
        
        print("2")
        new_document = {
                "season": season,
                "user_bong_data_archive": old_bong_data
            }
        print(new_document)

        try:
            await discord_server_database.insert_one(new_document)
        except Exception as e:
            print(e)

        print("3")
        try:
            await discord_server_database.update_one(
                {},
                {"$unset": {"user_bong_data": ""}}
            )
        except Exception as e:
            print(e)
    
    print("initalizing new season, database ready. Starting tasks shortly")

    await interaction.edit_original_response(content="The database has migrated. Bong tasks are now restarting")




#global commands
async def global_bongs(user_id):
    total_count=0
    for collection_name in await bongbotdatabase.list_collection_names():
        collection = bongbotdatabase[f'{collection_name}']
        documents = collection.find({
            "$or": [
                {f"user_bong_data.{user_id}": {"$exists": True}},
                {f"user_bong_data_archive.{user_id}":{"$exists": True}}
            ]
        })
        print("4")
        
        async for doc in documents:
            if doc and 'user_bong_data' in doc and f'{user_id}' in doc['user_bong_data']:
                total_count += doc['user_bong_data'][f'{user_id}']["bongs"]
            
            if doc and 'user_bong_data_archive' in doc and f'{user_id}' in doc['user_bong_data_archive']:
                total_count += doc['user_bong_data_archive'][f'{user_id}']["bongs"]
    
    return total_count

async def global_reactiontime(user_id):
    for collection_name in await bongbotdatabase.list_collection_names():
        collection = bongbotdatabase[f'{collection_name}']
        documents = collection.find({
            "$or": [
                {f"user_bong_data.{user_id}": {"$exists": True}},
                {f"user_bong_data_archive.{user_id}":{"$exists": True}}
            ]
        })
        
        async for doc in documents:
            if doc and 'user_bong_data' in doc and f'{user_id}' in doc['user_bong_data']:
                reaction_time = doc['user_bong_data'][f'{user_id}']["reaction_time"]
            
            if doc and 'user_bong_data_archive' in doc and f'{user_id}' in doc['user_bong_data_archive']:
                if reaction_time > doc['user_bong_data_archive'][f'{user_id}']["reaction_time"]:
                    reaction_time = doc['user_bong_data_archive'][f'{user_id}']["reaction_time"]
                
    if reaction_time is None:
        reaction_time = 0

    return reaction_time




async def drop_collection(guild):
    discord_server_database = bongbotdatabase[f'{guild}']
    
    discord_server_database.drop()
