import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, date
import database
from discord.ui import Modal, TextInput
from discord.utils import get
import validation
import time
import task_scheduler
#refresh button
class refresh_button_leaderboard(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="refresh", style=discord.ButtonStyle.green, custom_id="refresh_leaderboard")
    async def refresh_button_leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
            from interact import highestbongs
            button.disabled = True
            old_message = await interaction.channel.fetch_message(interaction.message.id)
            embed = await highestbongs(interaction, interaction.guild.id)
            await old_message.edit(embed=embed, view=self)
            await interaction.response.send_message("Leaderboard Refreshed", ephemeral=True)
            await asyncio.sleep(60)
            button.disabled = False
            await old_message.edit(view=self)

#refresh button for fastest times. Shows up on Admin command runners only
class refresh_button_fastesttimes(discord.ui.View):
    def __init__(self):
            super().__init__(timeout=None) 
    
    @discord.ui.button(label= "refresh", style=discord.ButtonStyle.green, custom_id="refresh_fastest_times")
    async def refresh_button_fastesttimes(self, interaction: discord.Interaction, button: discord.ui.Button):
            from interact import fastesttimes
            button.disabled = True
            old_message = await interaction.channel.fetch_message(interaction.message.id)
            embed = await fastesttimes(interaction, interaction.guild.id)
            await old_message.edit(embed=embed, view=self)
            await interaction.response.send_message("Fastest Times Refreshed", ephemeral=True)
            await asyncio.sleep(60)
            button.disabled = False
            await old_message.edit(view=self)

#class refresh_button_globalleaderboard(discord.ui.View):
    #def __init__(self):
            #super().__init__(timeout=None)
    
    #@discord.ui.button(label= "refresh", style=discord.ButtonStyle.green, custom_id="refresh_button_globalleaderboard")
    #async def refresh_button_globalleaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
            #from interact import guildleaderboard
            #from main import bot
            #button.disabled = True
            #old_message = await interaction.channel.fetch_message(interaction.message.id)
            #embed = await guildleaderboard(bot, interaction)
            #await old_message.edit(embed=embed, view=self)
            #await interaction.response.send_message("Guild Leaderboard Refreshed", ephemeral=True)
            #await asyncio.sleep(60)
            #button.disabled = False
            #await old_message.edit(view=self)


class Setup(Modal):
    def __init__(self):
        super().__init__(title="Server Setup")

        #self.bong_bot_golden_bong = TextInput(
            #label='Should the golden bong feature be enabled?', 
            #placeholder="True or False", 
            #custom_id="bong_bot_golden_bong"
        #)
        self.lowest_role = TextInput(
            label="Lowest Role",
            custom_id="lowest_role",
            placeholder="channels you want the Golden Bong to run in (ID)"
        )
        self.time_keeper_role = TextInput(
            label='Time Keeper Role',
            custom_id="time_keeper_role",
            placeholder="bong winner of the hour role. (ID)"
        )
        self.bong_bot_time = TextInput(
            label='Bong Time',
            custom_id="bong_bot_time",
            placeholder="the minute that the automated bong takes place (00-59)",
            min_length=2,
            max_length=2
        )
        self.admin_role = TextInput(
            label='Admin Role',
            custom_id="admin_role",
            placeholder="the role that has access to run golden bongs (ID)"
        )
        self.bong_bot_channel_id = TextInput(
            label='Bong Channel',
            custom_id="bong_bot_channel_id",
            placeholder="The channel where the autmated bongs get sent (ID)"
        )

        #self.add_item(self.bong_bot_golden_bong)
        self.add_item(self.lowest_role)
        self.add_item(self.time_keeper_role)
        self.add_item(self.bong_bot_time)
        self.add_item(self.admin_role)
        self.add_item(self.bong_bot_channel_id)
    
    
    
    async def on_submit(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        guild = interaction.guild

        bong_bot_golden_bong = True 
        lowest_role = self.lowest_role.value
        time_keeper_role = self.time_keeper_role.value
        bong_bot_time = self.bong_bot_time.value
        admin_role = self.admin_role.value
        bong_bot_channel_id = self.bong_bot_channel_id.value

        if not (lowest_role.isdigit() and time_keeper_role.isdigit() and admin_role.isdigit() and bong_bot_channel_id.isdigit()):
            await interaction.response.send_message(
                "Response contains invalid characters. Please make sure that the Roles and Channels are IDs.",
                ephemeral=True
            )
            return

        if not int(bong_bot_time) < 0 and int(bong_bot_time) > 59:
             await interaction.response.send_message(
                  "The Bong Bot Time must be a number between 00-59. See https://bong.bot/setup.html for more info",
                  ephemeral=True
             )
             return
        validation_setup = {
            "Bong Channel": await validation.validate(guild, "channel", int(bong_bot_channel_id)),
            "Admin Role": await validation.validate(guild,"role", int(admin_role)),
            "Time Keeper Role": await validation.validate(guild, "role", int(time_keeper_role)),
            "Lowest Role": await validation.validate(guild, "role", int(lowest_role))
        }

        final_validation_failed = [val for val, res in validation_setup.items() if res == False]
        
        if final_validation_failed:
            hreadvalmessage = "Validation failed, the values provided for "
            combined_reasons = ", ".join(final_validation_failed)
            final_message = hreadvalmessage + combined_reasons + " are incorrect, please check to make sure that the bot has access to these channels/roles. See https://bong.bot/setup.html for more info"
            await interaction.response.send_message(final_message, ephemeral=True)
            return



        golden_bong_random_channels = await validation.golden_bong_channel_list(guild, int(lowest_role))

        if golden_bong_random_channels is [] or golden_bong_random_channels is None:
            await interaction.response.send_message("Hmm, looks like the role you provided for the Lowest Role entry does not have access to any channels. Please check your server hierarchy and try again")
            return
            

        await interaction.response.send_message(
        f"Your server configuration has been updated. Thanks for using BongBot!\n**Your bong channel:** <#{bong_bot_channel_id}>\n**Your Time Keeper Role:** <@&{time_keeper_role}>\n**Lowest Role:** <@&{lowest_role}>\n**Bong Minute:** 00:{bong_bot_time}\n**Your Admin Role:** <@&{admin_role}>",
        ephemeral=True
        )

        #if bong_bot_golden_bong.lower() not in ["true", "false"]:
            #await interaction.response.send_message(
                #"Make sure that the Golden Bong Function is either True or False!",
                #ephemeral=True
            #)
            #return

        
        
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
        
        global bong_tasks
        bong_tasks = task_scheduler.bong_tasks
        
        task_name_for_guild = f"guild_task_{guild_id}"

        if task_name_for_guild in bong_tasks:
            print(f"stopping task for guild {interaction.guild}")
            bong_tasks[task_name_for_guild].cancel()
            del bong_tasks[task_name_for_guild]
            await task_scheduler.reboot_guild(interaction, guild_id)
        else:
            print("error refreshing, or new guild. starting new task")
            await task_scheduler.reboot_guild(interaction, guild_id)



async def embed_footer_format(guild):
     
    version = 3.0

    timestamp_format_os = "#"

    version_date = "5/16/2024"

    timestamp = datetime.now()

    actual_date=timestamp.strftime("%a, %b %d")

    actual_time=timestamp.strftime(f"%{timestamp_format_os}I:%M:%S %p")

    guild_name = guild.name

    guild_points = round(await database.get_points(guild.id), 2)


    localtime = list(time.localtime())
    
    if localtime[8] == 0:
        time_daylight_savings_status = "CST"
    else:
        time_daylight_savings_status = "CDT"


    return version, version_date, actual_date, actual_time, time_daylight_savings_status, guild_name, guild_points
    