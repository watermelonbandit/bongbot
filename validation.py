import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, date
import database
from discord.ui import Modal, TextInput
from discord.utils import get
import task_scheduler


async def validate(guild, medium, cid):
    if medium == "channel":
        channel = get(guild.channels, id=cid)
        if channel is None:
            return False
   
    if medium == "role":
        role = get(guild.roles, id=cid)
        if role is None:
            return False


    if medium == "user":
        user = get(guild.members, id=cid)
        if user is None:
            return False 



async def golden_bong_channel_list(guild, lowest_role):
    
    text_channels_list = []
    
    for channel in guild.channels:
        if str(channel.type) == 'text':
            target_role = discord.utils.get(guild.roles, id=lowest_role)
            if target_role and channel.permissions_for(target_role).send_messages:
                text_channels_list.append(str(channel.id))

    return text_channels_list


async def validate_admin_role_access(interaction, user: discord.Member):
    guild_id = interaction.guild.id
    admin_role = await database.get_admin_role(guild_id)
    
    role = discord.utils.find(lambda r: r.id == admin_role, interaction.guild.roles)

    if role in user.roles:
        return True
    else:
        return False, role


async def permissions_error(interaction, role):
    embed = discord.Embed(
        title="Permissions Error",
        description="**You dont have the required role for this command.**\nIf you are a server administrator, check your configuration and try again.",
        color=discord.Color.red()
    )

    embed.set_footer(text=f"error 1 - missing permissions. expecting {role} in {interaction.user} roles, found none")
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup_validation(bong_bot_golden_bong,lowest_role,time_keeper_role,bong_bot_time,admin_role,bong_bot_channel_id,guild,guild_id,interact):

    
    if not int(bong_bot_time) < 00 and int(bong_bot_time) > 59:
        return 2
    
    if not bong_bot_time.startswith("0") and int(bong_bot_time) < 10:
        bong_bot_time = "0" + str(bong_bot_time)
        
    print("3")
    validation_setup = {
        "Bong Channel": await validate(guild, "channel", int(bong_bot_channel_id)),
        "Admin Role": await validate(guild,"role", int(admin_role)),
        "Time Keeper Role": await validate(guild, "role", int(time_keeper_role)),
        "Lowest Role": await validate(guild, "role", int(lowest_role))
    }
    print("4")
    final_validation_failed = [val for val, res in validation_setup.items() if res == False]
    
    if final_validation_failed:
        return final_validation_failed, "verif-failed"
    print("5")
    
    golden_bong_random_channels = await golden_bong_channel_list(guild, int(lowest_role))

    print("6")
    if golden_bong_random_channels is [] or golden_bong_random_channels is None:
        return "golden bong verif failed"
        

    #if bong_bot_golden_bong.lower() not in ["true", "false"]:
        #await interaction.response.send_message(
            #"Make sure that the Golden Bong Function is either True or False!",
            #ephemeral=True
        #)
        #return
    print("7")   
    
    await database.server_setup(
    guild_id,
    bong_bot_channel_id,
    lowest_role,
    bong_bot_golden_bong,
    time_keeper_role,
    admin_role,
    bong_bot_time
    )

    await asyncio.sleep(5)

    await database.server_goldenbong_channellist(guild_id, golden_bong_random_channels)

    await task_scheduler.restart_on_config_update(interact,guild_id)

    return "Passed"