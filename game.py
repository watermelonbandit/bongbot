import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timezone, date
import database
from discord.ui import Modal, TextInput
from discord.utils import get
import validation
import time
import random
import database
import requests
import keys 

fake_clock_emojis = ['🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛', '🕜', '🕝', '🕞', '🕟', '🕠', '🕡', '🕢', '🕣', '🕤', '🕥', '🕦', '🕧']
april_fools_mode= False 
debug_mode= False
season = "Pre - 1"
bong_goal = 100

async def bong(bot, time_keeper_role, guild_id, channel_id, current_ending):
    current_time = datetime.now().strftime("%H:%M")
    current_time_stamp = int(time.time())
    preperiod_triggered = False
    if current_time.endswith(current_ending) or debug_mode == True:
        #double check that double/triple bongs are not happening when api craps out
        last_bong_time = await database.get_last_bong_time(guild_id)
        if last_bong_time is not None:
            diff = current_time_stamp - last_bong_time
            print(diff)
            if diff < 3660:
                print("Discord instablity has caused double bongs. cancelling task")
                return
 
        blacklist = await database.get_server_blacklist(guild_id)
        print(f"Bong for guild: {guild_id}")
        
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        delay = random.randint(1, 10)
        await asyncio.sleep(delay)
        global preperiod
        preperiod = True
        try:
            fakeclocks = random.randint(0,4)
            sleepytime= random.randint(2,4)
            total_anti_cheat_checktime = fakeclocks * sleepytime
           
            bong_message = await channel.send("Bong")
            bong_message_id = bong_message.id
            loop = tasks.loop(count=1)(check_early_bong_reactions)
            loop.start(bot, bong_message_id, int(channel_id), int(guild_id), total_anti_cheat_checktime)

            for c in range(fakeclocks):
                await bong_message.add_reaction(random.choice(fake_clock_emojis))
                await asyncio.sleep(sleepytime)
        except:
            return

        preperiod = False
        loop.stop()
        if preperiod_triggered == False:
            await bong_message.add_reaction(bong_emoji)
            timestartreaction = time.perf_counter()

            try:
                _, user = await bot.wait_for(
                    "reaction_add",
                    check=lambda r, u: str(r.emoji) == bong_emoji
                    and not u.bot
                    and bong_message_id == r.message.id,
                    timeout=60,
                    )

                tsr = time.perf_counter()
                try:
                    await bong_message.delete()
                except:
                    print("Anti Cheat activated, exiting bong function")
                    return
                
                reaction_time = tsr - timestartreaction
                timestartreaction = 0
                print(f"{user} got the bong in {guild.name}")
                
                #if check_blacklist(user) == False:
                if str(user.id) not in blacklist:
                    await announce_winner(guild_id, channel, user, reaction_time)
                    
                else:
                    await channel.send(f"{user.mention} has been blacklisted.")

            except asyncio.TimeoutError:
                await bong_message.delete()
                print("No one got the bong")
                time_keeper_role = discord.utils.get(channel.guild.roles, id=time_keeper_role)
                for member in time_keeper_role.members:
                    await member.remove_roles(time_keeper_role)
               

        else:
            return
        
    
#goldenbong stuff 
async def golden_bong_message(bot, interaction):
    
    text_channels_list = await database.return_goldenbong_channelist(interaction.guild.id)
    
    print(text_channels_list)

    try:    
        random_channel = random.choice(text_channels_list)
    except Exception as e:
        print(e)

    print(random_channel)
    
    bong_channel_id = await database.get_channel(interaction.guild.id)

    blacklist = await database.get_server_blacklist(interaction.guild.id)

    print("got here")

    if bong_channel_id == "Not Here" or bong_channel_id is None:
        interaction.response.send_message("I couldnt find a bong channel, please check to make sure that your guild is configured correctly. see HELP PAGE for more.")
    
    if random_channel is None or text_channels_list == "Not Here":
        interaction.response.send_message("Hmm, there appears to be a issue with your configuration, double check to make sure that your guild configuration is correct, or try again later")
        return
    
    channel = interaction.guild.get_channel(int(random_channel))
    og_channel = interaction.guild.get_channel(bong_channel_id)
    try:
        bong_message1 = await channel.send("Golden Bong!")
        await interaction.edit_original_response(content="Golden Bong Starting Now")
        async with og_channel.typing():
            bong_message_id = bong_message1.id
            await bong_message1.add_reaction("🐸")
            timestartreaction = time.perf_counter()
            _, user = await bot.wait_for(
                "reaction_add",
                check=lambda r, u: str(r.emoji) == "🐸"
                and not u.bot
                and bong_message_id == r.message.id,
                timeout=10,
                )
            tsr = time.perf_counter()
            await bong_message1.delete()
            
            reaction_time = tsr - timestartreaction
            timestartreaction = 0 
            goldenbong=True

            if user.id == interaction.user.id:
                await og_channel.send(f"Anti Corruption Activated: {user.mention} cannot call the command and get the golden bong! Nice try.")
                return

            elif str(user.id) not in blacklist:
                await announce_winner(interaction.guild.id, og_channel, user, reaction_time, goldenbong, channel)
                await asyncio.sleep(5)
                await golden_bong(interaction, channel, user)

            else:
                await og_channel.send(f"{interaction.user.mention} has been blacklisted.")
                return
    
    except asyncio.TimeoutError:
        await bong_message1.delete()
        if channel:
            await og_channel.send(f"Too Slow! The Golden Bong was in {channel.mention}. Better luck next time!")
            


async def golden_bong(interaction, channel, member):
    
    leaderboard = await database.get_server_data(interaction.guild.id)

    golden_bongs = leaderboard[str(member.id)]['golden_bongs']

    if str(member.id) in leaderboard:
        if golden_bongs:
            golden_bong_1 =  golden_bongs + 1
            leaderboard[str(member.id)]['golden_bongs'] = int(golden_bong_1)
        else:
            golden_bongs_inital = 1
            print(leaderboard[str(member.id)]['golden_bongs']) 
            leaderboard[str(member.id)]['golden_bongs'] = int(golden_bongs_inital)

        golden_bongs_display = leaderboard[str(member.id)]['golden_bongs']
        await asyncio.sleep(5)
        rtime = int(time.time()) + 5
        golden_bong_annoucement = await channel.send(f"You got a golden bong! Use the snipe command to snipe anyones bongs. The power you have is immense. Use it wisely. This message will disappear <t:{rtime}:R>")
        await asyncio.sleep(4)
        await golden_bong_annoucement.delete()
        print("updating server users now")
        await database.update_server_users(interaction.guild.id, leaderboard)
    

#The main annouce_winner, slighty adapted to correctly pull data from the database
async def announce_winner(guild_id, channel, member, reaction_time, goldenbong=None, special_channel=None):
    bong_time = int(time.time())

    leaderboard = await database.get_server_data(guild_id)
    streak = await database.get_streak(guild_id)
    time_keeper_role_id = await database.get_time_keeper_role(guild_id)
    #bong_goal = await database.get_bong_goal(guild_id)
    reaction_time_rounded = round((reaction_time),2)

    if time_keeper_role_id in [role.id for role in member.roles]:
        if streak == "Not here":
            streak = 1
        else:
            streak +=1

        points = await calculate_points(guild_id, reaction_time)

        if str(member.id) in leaderboard:
            if 'reaction_time' in leaderboard[str(member.id)]:
                prev_reaction_time = leaderboard[str(member.id)]['reaction_time']
                if reaction_time < prev_reaction_time:
                    leaderboard[str(member.id)]['reaction_time'] = reaction_time
            else:
                leaderboard[str(member.id)]['reaction_time'] = reaction_time

            leaderboard[str(member.id)]['bongs'] += 1
        
        else:
            leaderboard[str(member.id)] = {'bongs': 1, 'reaction_time': reaction_time}

        
        if leaderboard[str(member.id)]['bongs'] == bong_goal:
            timestamp = int(time.time())
            leaderboard[str(member.id)]['time_69_bongs'] = timestamp
            await channel.send(f"{member.mention}, Nice")
    

        elif leaderboard[str(member.id)]['bongs'] > bong_goal:
            leaderboard[str(member.id)]['bongs'] = 0
            await channel.send(f"{member.mention} congratulations. You played yourself. Your score has been reset to 0")
            await database.update_server_users(guild_id, leaderboard)
            return
        
        elif goldenbong is not None:
            await channel.send(f"**Golden Bong Alert!** {member.mention} found the Golden Bong in {special_channel.mention}.\n{member.mention} continues the bong with a reaction time of **{str(reaction_time_rounded)}** seconds. They are on a **{str(streak)}** bongs streak!\nPoints added: +**{round(points, 2)}**")
            gb_timestamp = int(time.time())
            sc_channel = special_channel.mention
            gb_user = member
            await database.dynamic_resource(guild_id, gb_timestamp, sc_channel, str(member.id))


        else:
            await channel.send(
                f"{member.mention} continues the bong with a reaction time of **{str(reaction_time_rounded)}** seconds.\nPoints added: +**{round(points, 2)}**")
        
        await database.streak(guild_id, streak)

        await database.update_server_users(guild_id, leaderboard, bong_time)

    else:
        # Check if there's a previous winner with the time_keeper_role_id
        
        streak = 1
        
        await database.streak(guild_id, streak)

        points =  await calculate_points(guild_id, reaction_time)

        previous_winner = None

        for guild_member in channel.guild.members:
            if time_keeper_role_id in [role.id for role in guild_member.roles]:
                previous_winner = guild_member
                break

        if previous_winner:
            previous_time_keeper_role = discord.utils.get(previous_winner.roles, id=time_keeper_role_id)
            await previous_winner.remove_roles(previous_time_keeper_role)

        reaction_time_rounded = round((reaction_time),2)
    
        if str(member.id) in leaderboard:
            if 'reaction_time' in leaderboard[str(member.id)]:
                prev_reaction_time = leaderboard[str(member.id)]['reaction_time']
                if reaction_time < prev_reaction_time:
                    leaderboard[str(member.id)]['reaction_time'] = reaction_time
            else:
                leaderboard[str(member.id)]['reaction_time'] = reaction_time

            leaderboard[str(member.id)]['bongs'] += 1
        
        else:
            leaderboard[str(member.id)] = {'bongs': 1, 'reaction_time': reaction_time}

        if leaderboard[str(member.id)]['bongs'] == bong_goal:
            timestamp = int(time.time())
            leaderboard[str(member.id)]['time_69_bongs'] = timestamp
            await channel.send(f"{member.mention}, Nice")
            
        elif leaderboard[str(member.id)]['bongs'] > bong_goal:
            leaderboard[str(member.id)]['bongs'] = 0
            await channel.send(f"{member.mention} congratulations. You played yourself. Your score has been reset to 0")

        elif goldenbong is not None:
            await channel.send(f"Golden Bong Alert! {member.mention} found the Golden Bong in {special_channel.mention}!\nCongratulations {member.mention}! **{member.display_name}** got the bong and took **{str(reaction_time_rounded)}** seconds to react.\nPoints added: +**{round(points, 2)}**")
            gb_timestamp = int(time.time())
            sc_channel = special_channel.mention
            gb_user = member
            time_keeper_role = discord.utils.get(member.guild.roles, id=time_keeper_role_id)
            await member.add_roles(time_keeper_role)
            await database.dynamic_resource(guild_id, gb_timestamp, sc_channel, member.id)
            
            await database.update_server_users(guild_id, leaderboard)

        else:
            await channel.send(
                f"Congratulations {member.mention}! **{member.display_name}** got the bong and took"
                f" **{str(reaction_time_rounded)}** seconds to react.\nPoints added: +**{round(points, 2)}**")
            time_keeper_role = discord.utils.get(member.guild.roles, id=time_keeper_role_id)
            await member.add_roles(time_keeper_role)
        
        await database.update_server_users(guild_id, leaderboard, bong_time)



async def check_early_bong_reactions(bot, bong_message_id, bong_channel_id, guild_id, sleepytime):
    guild = bot.get_guild(guild_id)
    bong_channel = guild.get_channel(bong_channel_id)

    if preperiod == True:
        if bong_message_id:
            try:
                bong_message = await bong_channel.fetch_message(bong_message_id)
            except:
                return
            
            bot_reaction = discord.utils.get(bong_message.reactions, emoji=bong_emoji, me=True)
            if bot_reaction and bot_reaction.count > 1:
                return
            try:
                _, user = await bot.wait_for(
                    "reaction_add",
                    check=lambda r, u: str(r.emoji) == bong_emoji and not u.bot and bong_message_id == r.message.id and preperiod == True,
                    timeout=sleepytime,
                    )
                await bong_message.delete()
                await bong_channel.send(f"{user.mention} has clicked the bong EARLY. Shame them!")
                return
            
            except asyncio.TimeoutError:
                return


async def user_voted(interaction: discord.Interaction):
    leaderboard = await database.get_server_data(interaction.guild.id)

    member = interaction.user

    if str(member.id) in leaderboard:
        if 'golden_bongs' in leaderboard[str(member.id)] is not None:
            print(leaderboard[str(member.id)]['golden_bongs'])
            golden_bong_1 =  leaderboard[str(member.id)]['golden_bongs'] + 1
            leaderboard[str(member.id)]['golden_bongs'] = golden_bong_1
        else:
            golden_bongs_inital = 1
            print(leaderboard[str(member.id)]['golden_bongs']) 
            leaderboard[str(member.id)]['golden_bongs'] = golden_bongs_inital



async def calculate_points(guild_id, reaction_time):

    old_points = await database.get_points(guild_id)

    if reaction_time <= 0.34:
        points = 100
    elif reaction_time < 30:
        points =  100 - (100 / (30 - 0.34)) * (reaction_time - 0.34)
    elif reaction_time < 59:
        points = (100 / (59 - 30)) * (reaction_time - 30)
    else:
        return 100
    
    if old_points != None:
        new_point_value = old_points + points
    else:
        new_point_value = points
    
    await database.update_server_points(guild_id, new_point_value)
    
    return points


@tasks.loop(minutes=5)
async def seasonal_bong_updater():

    global month
    global bong_emoji
    month = datetime.now().month
    day = datetime.now().day

    print("Checking Bong Emoji, Modes and DST")
    if month == 10:
        bong_emoji = "🎃"

    elif month == 11 and day >=23 or month == 12:
        bong_emoji = "🎄"
    
    elif month == 11:
        bong_emoji = "🦃"
    
    elif month == 1 and day == 1:
        bong_emoji = "🎉"
        return
    
    elif month == 7 and day == 4:
        bong_emoji = "🎇"
        return
    else:
        bong_emoji = "⏰"


    if month == 4 and day == 1:
        april_fools_mode = True
        print("april_fools_mode = Enabled")

    else:
        april_fools_mode = False

    
    async def getweather():
        city = "Chicago"
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={keys.open_api_weather_key}'
        response = requests.get(url)
        data = response.json()
        desc = str(data['weather'][0]['description'])   
        return desc
