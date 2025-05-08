import discord
import asyncio
import random
import json
import time
from discord.ext import commands, tasks
from datetime import datetime, timezone, date
from typing import Union, List
import keys
from discord import app_commands
import requests
import calendar
from interface import Setup
import keys
import interact
import game
import task_scheduler
import database
import validation
import pymongo
import interface

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.message_content = True
intents.guilds = True  # Enable the privileged message content intent

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None, case_insensitive=True)

debug_mode=True
guild = 1128870689311572109

#Start up bot
@bot.event
async def on_ready():
    print("Starting, Please Wait")
    await asyncio.sleep(5)


    await bot.tree.sync()
    #check database connect
    print("Connecting To Database")

    
    print("Loading Guild Configurations......")
    
    print("Im in:")
    
    for guild in bot.guilds:
        print(f"{guild.id} - {guild.name}")
    
    await task_scheduler.start_game(bot)

    print("Loading Buttons...")
    bot.add_view(interface.refresh_button_fastesttimes())
    bot.add_view(interface.refresh_button_leaderboard())


    #print(f"Guilds that have been initalized with Configuration {guilds}")
    
    #asyncio.sleep(25)

    print("Guild Configurations Loaded!")

    # set bong emoji, time and date

    print ("Setting Bong Emoji")

    game.seasonal_bong_updater.start()

    await bot.change_presence(activity=discord.Game('/setup and bong.bot'))


 
 # joining and leaving logic

@bot.event 
async def on_guild_join(guild):
    print(f"joining {guild.name}")

@bot.event 
async def on_guild_remove(guild):
    print(f"leaving {guild.name}")
    await task_scheduler.stop_task_on_leave(guild)
    await database.drop_collection(guild.id)
    # maybe database logic here, although this might be triggered when discord api errors out
#interactions - game (Admin Only Access)

#Golden Bong Functionality
#interact.py/admin.py
@bot.tree.command(name="rgb", description="run a golden bong")
async def golden_bong(interaction: discord.Interaction):
    permission_check = await validation.validate_admin_role_access(interaction, interaction.user)
    if permission_check == True:
        context = interaction
        rtime = int(time.time()) + 10
        await interaction.response.send_message(f"Golden Bong starting <t:{rtime}:R>", ephemeral=True)
        await asyncio.sleep(10)
        try:
            await game.golden_bong_message(bot, context)
        except discord.errors.Forbidden:
            await asyncio.sleep(3)
            await interaction.edit_original_response(content="Error. Please double check that the bot has the lowest role for this feature to work. Changed Channel/Role Permissions? run `/refresh` to update your guild.")
    else:
        await validation.permissions_error(interaction, permission_check[1])
#Blacklist Functionality - Add/Remove user from guild blacklist.
#admin.py
@bot.tree.command(name="blacklist", description="add/remove user to the blacklist")
@app_commands.choices(operation=[
    app_commands.Choice(name="add the user to the blacklist", value="add"),
    app_commands.Choice(name="remove the user to the blacklist", value="remove"),
])
async def blacklist(interaction: discord.Interaction, operation: app_commands.Choice[str], member: discord.Member, reason: str=None):
    permission_check = await validation.validate_admin_role_access(interaction, interaction.user)
    if permission_check == True:
        context = interaction
        await interact.blacklist(interaction.guild.id, context, operation, member, reason)


#Optional golden bong leaderboard functionality. Could be enabled for all users, admin only by defualt
#interact.py/admin.py
@bot.tree.command(name="goldenbongleaderboard", description="see the golden bong leaderboard")
async def goldenbongleaderboard(interaction: discord.Interaction):
    permission_check = await validation.validate_admin_role_access(interaction, interaction.user)
    if permission_check == True:
        context = interaction
        res = await interact.golden_bong_leaderboard(context)
        await interaction.response.send_message(embed=res)
    else:
        await validation.permissions_error(interaction, permission_check[1])

#Setup the bot 
#bong.py/interface.py
@app_commands.checks.has_permissions(administrator=True)
@bot.tree.command(name="setup", description="setup the bot for your server")
async def show_setup_modal(interaction: discord.Interaction, golden_bong: bool = False):
    #interaction.response.send_message("# Welcome to BongBot setup\n## Make sure that developer mode is enabled.\nYou will need the following:\n**BongBot Time**")
    modal = Setup()
    await interaction.response.send_modal(modal)


@app_commands.checks.has_permissions(administrator=True)
@bot.tree.command(name="fastsetup", description="fast setup with no modal")
async def fast_setup(interaction: discord.Interaction, bong_time: str, bong_channel: discord.TextChannel, admin_role: discord.Role,time_keeper_role: discord.Role, lowest_role: discord.Role, golden_bong: bool = False):
    
    await interaction.response.send_message("**Updating Server Config..........**", ephemeral=True)
    
    validate = await validation.setup_validation(golden_bong,lowest_role.id,time_keeper_role.id,bong_time,admin_role.id,bong_channel.id, interaction.guild, interaction.guild.id, interaction)
    
    if validate == 1:
        await interaction.edit_original_response(
            content="Response contains invalid characters. Please make sure that the Roles and Channels are IDs.",
        )    
        return
    if validate == 2:
        await interaction.edit_original_response(
            content="The Bong Bot Time must be a number between 00-59. See https://bong.bot/setup.html for more info",
        )
        return
    
    if "verif-failed" in validate[1]:
        hreadvalmessage = "Validation failed, the values provided for "
        combined_reasons = ", ".join(validate[0])
        final_message = hreadvalmessage + combined_reasons + " are incorrect, please check to make sure that the bot has access to these channels/roles. See https://bong.bot/setup.html for more info"
        await interaction.edit_original_response(content=final_message)
        return

    if "golden_bong_verif_failed" in validate:
        await interaction.edit_original_response(content="Hmm, looks like the role you provided for the Lowest Role entry does not have access to any channels. Please check your server hierarchy and try again")
        return

    if validate == "Passed":
        await interaction.edit_original_response(content=f"**Server Configuration has been successfully validated.**\nYour server configuration has been updated.Thanks for using BongBot!\n**Your Bong Channel:** <#{str(bong_channel.id)}>\n**Your Time Keeper Role:** <@&{str(time_keeper_role.id)}>\n**Lowest Role:** <@&{str(lowest_role.id)}>\n**Bong Minute:** 00:{bong_time}\n**Your Admin Role:** <@&{str(admin_role.id)}>")


#interactions - game (All User Access)

#this enables the snipe functinality
#interact.py/game.py
@bot.tree.command(name="snipe", description="snipe another users bongs")
async def snipe_command(interaction: discord.Interaction, member: discord.Member, notes: str):
    context = interaction
    await interact.snipe(context, member, notes)

#this returns the guild leaderboard of bongs
#interact.py
@bot.tree.command(name="highestbongs", description="see the highest bong count in your guild")
async def highestbongs(interaction: discord.Interaction):
    guild_id = int(interaction.guild.id)
    context = interaction
    embed = await interact.highestbongs(context, guild_id)
    user_verified = await validation.validate_admin_role_access(interaction, interaction.user)
    if user_verified == True:
        await interaction.response.send_message(embed=embed, view=interface.refresh_button_leaderboard())
    else:
        await interaction.response.send_message(embed=embed)
   
#this returns the fastest calulated times
#interact.py
@bot.tree.command(name="fastesttimes", description="See the servers fastest reaction times")
async def fastesttimes(interaction: discord.Interaction):
    guild_id = int(interaction.guild.id)
    context = interaction
    embed = await interact.fastesttimes(context, guild_id)
    user_verified = await validation.validate_admin_role_access(interaction, interaction.user)
    if user_verified == True:
        await interaction.response.send_message(embed=embed,view=interface.refresh_button_fastesttimes())
    else:
        await interaction.response.send_message(embed=embed)
    
#this returns the amount of bongs the user has in a guild.
#interact.py

@bot.tree.command(name="bongs", description="See how many bongs you (or another user) has")
async def get_user_bongs(interaction: discord.Interaction, member: discord.Member = None):
    guild_id= int(interaction.guild.id)
    context = interaction
    embed = await interact.b(guild_id, context, member)
    await interaction.response.send_message(embed=embed)


#this returns the current bong holder in your guild
#interact.py
@bot.tree.command(name="currentbongholder", description="see the current bong holder")
async def get_current_bong_holder(interaction: discord.Interaction):
    guild_id = int(interaction.guild.id)
    context = interaction
    res = await interact.currentbongholder(context, guild_id)

    if res == "Broken Configuration":
        interaction.response.send_message("It appears that you havent configured the bot correctly, or the bot has encountered a error. See HELP PAGE for more")
        return 
    
    await interaction.response.send_message(res)

#this is a command that refreshes the golden bong configuration channels incase the users/guild changes prevously saved channels/roles permissions. This is better than polling the discord api every 5 seconds for updates
@bot.tree.command(name="refresh", description="refresh golden bong configuration")
async def refresh_guild_configuration(interaction: discord.Interaction):
    permission_check = await validation.validate_admin_role_access(interaction, interaction.user)
    if permission_check == True:
        await interaction.response.send_message("Refreshing Golden Bong Channels, Please wait")
        lowest_role=await database.get_lowest_role(interaction.guild.id)
        golden_bong_random_channels = await validation.golden_bong_channel_list(interaction.guild, int(lowest_role))
        await database.server_goldenbong_channellist(interaction.guild.id, golden_bong_random_channels)
        await interaction.edit_original_response(content="Golden Bong Channels Updated")
    else:
        await validation.permissions_error(interaction, permission_check[1])
    

#this returns the last golden bong, where it was ran, and who got it.
#interact.py
@bot.tree.command(name="lastgoldenbong", description="check when the last golden bong was ran")
async def whengoldenbong(interaction: discord.Interaction):
    response = await database.get_golden_bong_info(interaction.guild.id)
    if response and response != "Not here":
        await interaction.response.send_message(f"The last golden bong was found in {response[0]} by <@{response[2]}>. It was found on <t:{response[1]}:f>, about <t:{response[1]}:R>")
    else:
        await interaction.response.send_message("No one has gotten a golden bong yet.")

#this returns the how many golden bongs a user has
#interact.py

@bot.tree.command(name="mygoldenbongs", description="see how many golden bongs you have")
async def howmanygoldenbongs(interaction: discord.Interaction):
    await interact.gb_personal(interaction)


@bot.tree.command(name="vote", description="vote for BongBot! Get a extra golden bong for doing so!")
async def vote(interaction: discord.Interaction):
    await interaction.response.send_message("Vote for Bong Bot Here! https://bong.bot/vote/topgg. Check back here for when the incentive is added for voting :)")

    await interact.vote(interaction.id, interaction.guild.id)

@bot.tree.command(name="globalleaderboard", description="See the global guild leaderboard")
async def gldb(interaction: discord.Interaction):
        embed = await interact.guildleaderboard(bot, interaction)
        #user_verified = await validation.validate_admin_role_access(interaction, interaction.user)
        #if user_verified == True:
            #await interaction.response.send_message(embed=embed,view=interface.refresh_button_globalleaderboard())
        #else:
            #await interaction.response.send_message(embed=embed)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="bongstats", description="See all of your bong stats across all servers")
@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def myusercommand(interaction: discord.Interaction) -> None:
    try:
        total_bongs = await database.global_bongs(int(interaction.user.id))

        fastest_reaction_time = await database.global_reactiontime(int(interaction.user.id))
        
        embed=await interact.global_stats(total_bongs, fastest_reaction_time)

        await interaction.response.send_message(embed=embed)
    
    except Exception as e:
        print (e)
        



#adminstration on my end
@bot.tree.command(name="newseason", description="no touchies")
async def newseason(interaction: discord.Interaction):
    try:
        if interaction.user.id == 297243048255946752:
            await interaction.response.send_message("Starting new season migration.")
            await task_scheduler.stop_all_tasks(interaction, "New Season")
        else:
            await interaction.response.send_message("I SAID NO TOUCHIES")
    except Exception as e:
        print(e)






#error handling

#catch database errors. if one happens, notify system channel and pause all bongs until human intervention

#catch bot interaction errors
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        embed = discord.Embed(
            title="Permissions Error",
            description="**You dont have the required permission for this command.**\nOnly Server Admins can setup the bot",
            color=discord.Color.red()
    )
        embed.set_footer(text=f"error 1 - missing permissions. expecting administrator permision in {interaction.user} roles, found none")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    if isinstance(error, pymongo.errors.AutoReconnect):
            if interaction:
                embed = discord.Embed(
                    title="Database Error",
                    description="**There was a error communicating with the database**\nThe last action was not saved.\nPlease Try again later",
                    color=discord.Color.red()
            )
                embed.set_footer(text=f"error 4 - database connection lost")

                await interaction.response.send_message(embed=embed, ephemeral=True)
            
    if isinstance(error, pymongo.errors.ConnectionFailure):    
        if interaction:
            embed = discord.Embed(
                title="Database Error",
                description="**There was a error communicating with the database**\nThe last action was not saved.\nPlease Try again later",
                color=discord.Color.red()
        )
            embed.set_footer(text=f"error 4 - database connection lost")

            await interaction.response.send_message(embed=embed, ephemeral=True)




            


bot.run(keys.bot_key)