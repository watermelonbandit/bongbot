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

        interact=interaction

        bong_bot_golden_bong = True 
        lowest_role = self.lowest_role.value
        time_keeper_role = self.time_keeper_role.value
        bong_bot_time = self.bong_bot_time.value
        admin_role = self.admin_role.value
        bong_bot_channel_id = self.bong_bot_channel_id.value


        await interaction.response.send_message("**Updating Server Config....**")
        
        validate = await validation.setup_validation(bong_bot_golden_bong,lowest_role,time_keeper_role,bong_bot_time,admin_role,bong_bot_channel_id, guild, guild_id, interact)

        if validate == 1:
            await interaction.edit_original_response(
                content="Response contains invalid characters. Please make sure that the Roles and Channels are IDs."
            )    
            return
        
        if validate == 2:
            await interaction.edit_original_response(
                content="The Bong Bot Time must be a number between 00-59. See https://bong.bot/setup.html for more info"
            )
            return
        
        if "verif-failed" in validate[1]:
            hreadvalmessage = "Validation failed, the values provided for "
            combined_reasons = ", ".join(validate[0])
            final_message = hreadvalmessage + combined_reasons + " are incorrect, please check to make sure that the bot has access to these channels/roles. See https://bong.bot/setup.html for more info"
            await interact.edit_original_response(content=final_message)
            return

        if "golden_bong_verif_failed" in validate:
            await interaction.edit_original_response(content="Hmm, looks like the role you provided for the Lowest Role entry does not have access to any channels. Please check your server hierarchy and try again")
            return

        if validate == "Passed":
            await interaction.edit_original_response(content=f"Your server configuration has been updated. Thanks for using BongBot!\n**Your bong channel:** <#{bong_bot_channel_id}>\n**Your Time Keeper Role:** <@&{time_keeper_role}>\n**Lowest Role:** <@&{lowest_role}>\n**Bong Minute:** 00:{bong_bot_time}\n**Your Admin Role:** <@&{admin_role}>")
            return

async def embed_footer_format(guild):
     
    version = 4.20

    timestamp_format_os = "#"

    version_date = "5/13/2025"

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
    

