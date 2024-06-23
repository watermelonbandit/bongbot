import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, date
import database
from discord.ui import Modal, TextInput
from discord.utils import get
import validation
import interface
import random
import game 
#responses to leaderboard requests
#database.py, main.py


#Retrieve and build the Leaderboard embed
async def highestbongs(interaction, guild_id):
    
    #get leaderboard for guild from ddtabase
    #database.py
    leaderboard = await database.get_server_data(guild_id)

    leaderboard_embed = discord.Embed(title="**Highest Bong Holders**", color=discord.Color.blue())

    print(leaderboard)
    if leaderboard != {}:
        leaderboard1 = {int(user_id): score for user_id, score in leaderboard.items()}

        print(leaderboard1)
                        
        sorted_leaderboard = sorted(leaderboard1.items(), key=lambda x: (x[1].get('time_69_bongs', float('inf')), -x[1]['bongs']), reverse=False)

        print(sorted_leaderboard)
        top_10 = sorted_leaderboard[:10]  # Get the top 10 leaders
        avatar_id = sorted_leaderboard[0][0]
        avatar_user = interaction.guild.get_member(int(avatar_id))

        print(avatar_user)

        if avatar_user.avatar:
            leaderboard_embed.set_thumbnail(url=avatar_user.avatar.url)
        
        for rank, (user_id, score) in enumerate(top_10, start=1):
            print(user_id)
            print("the code stops after this")
            
            member = interaction.guild.get_member(int(user_id))
            
            if member:
                member_name = member
                member_mention = member.mention

            else:
                member_name = f"{user_id}"
                member_mention = " "


            #if 'hasBeenOveridden' in leaderboard[str(member.id)]:
                #overide = "*"
            #else:
                #overide = " "
    
            bong_count = score['bongs']
            time_69_bongs = score.get('time_69_bongs')

            if time_69_bongs:
                timestamp = datetime.fromtimestamp(int(time_69_bongs))
                bong_timestamp = "Time: " + f"**{timestamp.strftime('%Y-%m-%d %H:%M:%S')}**"
            else:
                bong_timestamp = ""

            leaderboard_embed.add_field(name=f"**{rank}. {member_name}**", value=f"Bongs: **{bong_count}** \nProfile: {member_mention}\n{bong_timestamp}", inline=False)

        
    else:
        leaderboard_embed.add_field(name="No data", value="No bongs recorded yet.", inline=False)


    time_data = await interface.embed_footer_format(interaction.guild)



    leaderboard_embed.set_footer(text=f"BongBot version {time_data[0]} dev, {time_data[1]}\nRequested on {time_data[2]} at {time_data[3]} {time_data[4]}\n{time_data[5]} - Points: {time_data[6]}")


    return leaderboard_embed

#Calulate Fastest Times 

async def fastesttimes(interaction, guild_id):
    global leaderboard

    leaderboard = await database.get_server_data(guild_id)

    embed = discord.Embed(title="**Fastest Reaction Times**", color=discord.Color.blue())

    if leaderboard != {}:
        
        fastest_times = [(member, data['reaction_time']) for member, data in leaderboard.items() if 'reaction_time' in data]
        
        fastest_times.sort(key=lambda x: x[1]) 

        print(fastesttimes)
   
        avatar_id = fastest_times[0][0]
        avatar_user = interaction.guild.get_member(int(avatar_id))

        if avatar_user.avatar:
            embed.set_thumbnail(url=avatar_user.avatar.url)

        for i, (member_id, reaction_time) in enumerate(fastest_times[:10], start=1):
            member = interaction.guild.get_member(int(member_id))
            if member:
                member_name = member
                member_mention = member.mention
            else:
                member_name = f"{member_id}"
                member_mention = " "
    
            reaction_time_rounded = round((reaction_time),2)
    
            embed.add_field(name=f"**{i}. {member_name}**", value=f"Time: **{reaction_time_rounded}** seconds \nProfile: {member_mention}", inline=False)
    else:
        embed.add_field(name="**No data**", value="No times recorded yet", inline=False)

    
    time_data = await interface.embed_footer_format(interaction.guild)

    embed.set_footer(text=f"BongBot version {time_data[0]} dev, {time_data[1]}\nRequested on {time_data[2]} at {time_data[3]} {time_data[4]}\n{time_data[5]} - Points: {time_data[6]}")

    return embed

async def b(guild_id, interaction, member: discord.Member = None):

    leaderboard = await database.get_server_data(guild_id)

    time = await interface.embed_footer_format(interaction.guild)

    blacklist = await database.get_server_blacklist(guild_id)

    if not member:
        member = interaction.user
    
    elif isinstance(member, str):
        try:
            member = await commands.MemberConverter().convert(interaction, member)
        except commands.MemberNotFound:
            await interaction.response.send_message("Invalid member specified.")
            return
    
    member_id = str(member.id)

    if member_id not in blacklist:
        if member_id in leaderboard:
            bong_count = leaderboard[member_id]['bongs']


            if 'reaction_time' in leaderboard[member_id]:
                reaction_time = round((leaderboard[member_id]['reaction_time']),2)
                reaction_time_str = f"Fastest Reaction Time: **{reaction_time}** seconds"

        
            elif bong_count == 0:
                await interaction.response.send_message(f"{member.display_name} has no bongs. This might be for a couple of reasons, including:\n**Clicking the Bong too early**\n**Getting Sniped**")
                return
            else:
                reaction_time_str = "No reaction time recorded yet."

            embed = discord.Embed(
                title=f"{member.display_name}",
                description=f"Bong Count: **{bong_count}**\n"
                            f"{reaction_time_str}\n",
                color=discord.Color.blue()
            )
            

            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
            
            return embed
        
        else:
            embed = discord.Embed(
                title=f"{member.display_name}",
                description=f"Bong Count: **0**\n",
                color=discord.Color.red()
            )
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

            return embed
    else:
        display_reason = blacklist[member_id]['reason']

        embed = discord.Embed(
                title=f"{member.display_name}",
                description=f"**This user has been blacklisted from the bot**\n**Reason:** {display_reason}",
                color=discord.Color.red()
            )
        
        if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

        return embed


async def currentbongholder(interaction, guild_id):
    
    time_keeper_role_id = await database.get_time_keeper_role(guild_id)

    print(time_keeper_role_id)

    if time_keeper_role_id == "Not Here":
        return "Broken Configuration"

    if time_keeper_role_id is not None:
        
        time_keeper_role = interaction.guild.get_role(int(time_keeper_role_id))
        
        print(time_keeper_role)
        
        time_keeper_member = discord.utils.get(time_keeper_role.members)
        
        if time_keeper_member is not None:
            return f"The current bong holder is {time_keeper_member.display_name}."
        
        else:
            return f"No one currently has the bong."
    
    else:
        return "The time keeper role has not been set."
    

async def blacklist(guild_id, interaction, operation, member, reason = None):
    
    blacklist = await database.get_server_blacklist(guild_id)

    if blacklist is None:
        blacklist = {}

    if member.id == interaction.user.id:
       await interaction.response.send_message("You cannot blacklist yourself")
       return
    
    elif isinstance(member, str):
        try:
            member = await commands.MemberConverter().convert(interaction, member)
        except commands.MemberNotFound:
            await interaction.response.send_message("Invalid member specified.")
            return
    
    if (operation.value == "add"):
        if str(member.id) in blacklist:
            await interaction.response.send_message(f"{member.mention} is already in the blacklist")
            return
        else:
            if reason:
                blacklist[str(member.id)] = {'reason': reason}
            else:
                reason = str("not recorded")
                
            blacklist[str(member.id)] = {'reason': reason}

            await interaction.response.send_message(f"{member.mention} has been blacklisted. Reason: {reason}")

            await database.update_server_blacklist(guild_id, blacklist)            
        

    if (operation.value) == "remove":
        if str(member.id) not in blacklist:
            await interaction.response.send_message(f"{member} is not currently blacklisted")
            return
    
        blacklist.pop(str(member.id))

        if not reason:
            reason = "not recorded"

            await interaction.response.send_message(f"{member.mention} has been removed from the blacklist. **Reason:** {reason}")
    
            await database.update_server_blacklist(guild_id, blacklist)



async def golden_bong_leaderboard(interaction):

    leaderboard = await database.get_server_data(interaction.guild.id)

    print(leaderboard)

    leaderboard_embed = discord.Embed(title="**Secret Golden Bong Leaderboard**", color=discord.Color.blue())
    
    if leaderboard is not {}:
        sorted_leaderboard = [
            user for user in sorted(
                leaderboard.items(),
                key=lambda x: -(x[1].get('golden_bongs') or 0)
            ) if 'golden_bongs' in user[1] and user[1]['golden_bongs'] is not None and user[1]['golden_bongs'] > 0 
        ]

        if sorted_leaderboard:
            top_10 = sorted_leaderboard[:10]  
            avatar_id = sorted_leaderboard[0][0]
            avatar_user = interaction.guild.get_member(int(avatar_id))

            if avatar_user.avatar:
                leaderboard_embed.set_thumbnail(url=avatar_user.avatar.url)
            
            for rank, (user_id, score) in enumerate(top_10, start=1):
                member = interaction.guild.get_member(int(user_id))
                if member:
                    member_name = member
                    member_mention = member.mention

                else:
                    member_name = f"{user_id}"
                    member_mention = " "
                
                bong_count = score['golden_bongs']



                leaderboard_embed.add_field(name=f"**{rank}. {member_name}**", value=f"Golden Bongs: **{bong_count}**\nProfile: {member_mention}", inline=False)

    
        else:
            leaderboard_embed.add_field(name="No data", value="No bongs recorded yet.", inline=False)
    
    
    time_data = await interface.embed_footer_format(interaction.guild)

    
    
    leaderboard_embed.set_footer(text=f"BongBot version {time_data[0]} dev, {time_data[1]}\nRequested on {time_data[2]} at {time_data[3]} {time_data[4]}\n{time_data[5]} - Points: {time_data[6]}")


    return leaderboard_embed
    


async def gb_personal(interaction):
    user = interaction.user.id
    leaderboard = await database.get_server_data(interaction.guild.id)
    
    if leaderboard is not {} or leaderboard is not None:
        if 'golden_bongs' in leaderboard[str(user)]:
            goldenbongs = leaderboard[str(user)]['golden_bongs']
            if goldenbongs is not None:
                await interaction.response.send_message(f"You have {goldenbongs} golden bongs", ephemeral=True)
            else:
                await interaction.response.send_message(f"You have 0 golden bongs", ephemeral=True)
            
        await interaction.response.send_message(f"You have 0 golden bongs", ephemeral=True)
    
    await interaction.response.send_message(f"You have 0 golden bongs", ephemeral=True)




async def snipe(interaction,  member: discord.Member, notes: str):
    leaderboard = await database.get_server_data(interaction.guild.id)
        
    if leaderboard is not {}:
        if isinstance(member, str):
            try:
                member = await commands.MemberConverter().convert(interaction, member)
            except commands.MemberNotFound:
                await interaction.response.send_message("Invalid member specified.")
                return   
            
        if str(member.id) not in leaderboard:
            await interaction.response.send_message(f"**{member.mention} has not interacted with the bot. Try again**")
            return 
        
        if 'golden_bongs' not in leaderboard[str(interaction.user.id)]:
            await interaction.response.send_message(f"**{interaction.user.mention} doesnt have any golden bongs**")
            return
            

        member_bong_count = leaderboard[str(member.id)]['bong_count']
        shooter_gbong_count = leaderboard[str(interaction.user.id)]['golden_bongs']

        bullet = random.randint(5,15)

        weather = await game.getweather()

        if 'mist' in weather:
            bullet = random.randint(5,30)

        elif 'rain' in weather:
            bullet = random.randint(5,42)
        
        elif 'dust' in weather:
            bullet = random.randint(5,50)
        
        elif 'tornado' in weather:
            bullet = 69
            eligible_for_nuke=True
        
        if shooter_gbong_count >= 1:
            if member_bong_count >= 1:
                
                if member_bong_count == 69 and eligible_for_nuke == False:
                    await interaction.response.send_message("You cannot snipe a user that has reached 69 bongs")
                    return
                
                if bullet == 69 and eligible_for_nuke == True:
                    await interaction.response.send_message(f"{member.mention} has been nuked by {interaction.user.mention}\n {interaction.user.mention}'s message to {member.mention}\n **{notes}")
                    leaderboard.pop(str(member.id))
                    await database.update_server_users(interaction.guild.id)
                    return
                
                if member_bong_count < bullet:
                    leaderboard[str(member.id)]['old_bong_count'] = member_bong_count
                    leaderboard[str(member.id)]['bong_count'] = 0
                    member_bong_count_new = 0
                    member_bongs_lost = member_bong_count
                else:
                    member_bong_count_new = member_bong_count - bullet
                    leaderboard[str(member.id)]['old_bong_count'] = member_bong_count
                    leaderboard[str(member.id)]['bong_count'] = member_bong_count_new
                    member_bongs_lost = bullet

                shooter_gbong_count_new = shooter_gbong_count - 1
                leaderboard[str(interaction.user.id)]['golden_bongs'] = shooter_gbong_count_new

                embed = discord.Embed(
                    title="Someone got sniped!",
                    description=f"**User:**{member.mention}\n"
                                f"**Previous Bong Count:** {member_bong_count}"
                                f"**New Bong Count** {member_bong_count}"
                                f"**Bongs Lost** {member_bongs_lost}"
                                f"**Message From {interaction.user.mention}:** {notes}",
                        color = discord.Color.red()
                    )
                
                await interaction.response.send_message(embed=embed)
            
            else:
                await interaction.response.send_message(f"**{member.mention} has 0 bongs. Try again**")
        else:
            await interaction.response.send_message(f"**{interaction.user} doesnt have any golden bongs**")

        
        await database.update_server_users(interaction.guild.id)





async def guildleaderboard(bot, interaction):

    global_leaderboard = await database.get_global_points()
    
    leaderboard_embed = discord.Embed(title="**Highest Guilds**", color=discord.Color.blue())

    if global_leaderboard != "Not Here" or global_leaderboard != []:
        leaderboard1 = {score for guild_id, score in global_leaderboard.items()}
        print("this is the sorted leaderboard")
        print(leaderboard1)
                        
        sorted_leaderboard = sorted(global_leaderboard.items(), key=lambda item: item[1], reverse=True)

        if sorted_leaderboard:
            top_10 = sorted_leaderboard[:10]  
            avatar_id = sorted_leaderboard[0][0]
            avatar_user = bot.get_guild(int(avatar_id))
            avatar = avatar_user.icon.url

            if avatar:
                leaderboard_embed.set_thumbnail(url=avatar)

        print(sorted_leaderboard)
        top_10 = sorted_leaderboard[:10]  
        
        for rank, (guild_id, points) in enumerate(top_10, start=1):
            
            print(guild_id)
            
            guild_obj = bot.get_guild(int(guild_id))
            
            if guild_obj:
                guild_name = guild_obj.name

            else:
                guild_name = f"{guild_id}"                

            p = points

            print(points)            

            leaderboard_embed.add_field(name=f"**{rank}. {guild_name}**", value=f"Points: **{round(p, 2)}**", inline=False)

            print("got past here")

        
    else:
        leaderboard_embed.add_field(name="No data", value="A bot error has occured", inline=False)


    time_data = await interface.embed_footer_format(interaction.guild)


    leaderboard_embed.set_footer(text=f"BongBot version {time_data[0]} dev, {time_data[1]}\nRequested on {time_data[2]} at {time_data[3]} {time_data[4]}\n{time_data[5]} - Points: {time_data[6]}")


    return leaderboard_embed




