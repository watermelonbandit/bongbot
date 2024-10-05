import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, date
import database
from discord.ui import Modal, TextInput
from discord.utils import get


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
