import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timezone, date
import database
from discord.ui import Modal, TextInput
from discord.utils import get
import validation
import game
import database


bong_tasks = {}

async def start_game(bot):
    global context
    context = bot
    
    guild_data = await database.get_server_ids()

    for guild_id in guild_data:
            if guild_id != "init" and guild_id != None:
                time_keeper_role = await database.get_time_keeper_role(guild_id)
                bong_channel_id = await database.get_bong_channel_id(guild_id)
                current_time = ":" + await database.get_bong_time(guild_id)
                
                task_name = f"guild_task_{guild_id}"
                        
                loop = tasks.loop(seconds=60)(game.bong)
                
                loop.start(context, time_keeper_role, int(guild_id), int(bong_channel_id), current_time)

                bong_tasks[task_name] = loop

        

async def reboot_guild(interaction, guild_id):
    time_keeper_role = await database.get_time_keeper_role(guild_id)
    bong_channel_id = await database.get_bong_channel_id(guild_id)
    current_time = ":" + await database.get_bong_time(guild_id)
            
    task_name = f"guild_task_{guild_id}"
            
    
    print(f"Starting Task for guild {interaction.guild}")
    loop = tasks.loop(seconds=60)(game.bong)
    loop.start(context, int(time_keeper_role), int(guild_id), int(bong_channel_id), current_time)
    
    bong_tasks[task_name] = loop



async def stop_all_tasks(interaction = None, mode = None):
    print("Stopping all Bong Tasks")
    print("1")
    for task_name, task in bong_tasks.items():
        task.cancel()
    print ("2")
    await asyncio.sleep(10)
    
    if interaction and mode == "New Season":
        await interaction.edit_original_response(content ="All bong tasks have stopped.")
        await asyncio.sleep(30)
        print("Now starting database migration")
        await database.move_user_bong_data(interaction, game.season)
        await asyncio.sleep(5)
        await start_game(context)
        await interaction.edit_original_response(content="BongBot is now in a ready state")

async def stop_task_on_leave(guild):
    task_name_for_guild = f"guild_task_{guild.id}"

    if task_name_for_guild in bong_tasks:
        print(f"stopping task for guild {guild.id}")
        bong_tasks[task_name_for_guild].cancel()
        del bong_tasks[task_name_for_guild]
             
    

