from __future__ import print_function
from cProfile import label
from email import message
from errno import EPERM
from gettext import find
import json
import requests
from lib2to3.pytree import convert
from msilib.schema import File, TextStyle
from socket import timeout
from tkinter import Button
import requests
from requests_oauthlib import OAuth1Session
import os
from datetime import datetime, timedelta
from asyncio import sleep as s, wait
# from webserver import keep_alive
import discord
from discord.ext import tasks, commands
import discord.ext
from discord import Intents
from discord import app_commands
from discord import colour
from discord import Streaming
from discord.utils import get
import discord
from discord import app_commands, ui
import tweepy
import http.client
from dotenv import load_dotenv
load_dotenv()


class Role_Buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Role 1', style=discord.ButtonStyle.gray, emoji='❓', custom_id='STRL:RoleButton1')
    async def Role1(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = client.get_guild(interaction.guild_id)
        if guild is None:
        # Check if we're still in the guild and it's cached.
            print("Guild None")
            return
        role = guild.get_role(986714816200712223)
        if role is None:
        # Make sure the role still exists and is valid.
            print("Role Doesn't Exist")
            return
        if role in interaction.user.roles:
            try:
        # Finally, remove the role.
                await interaction.user.remove_roles(role)
            except discord.HTTPException:
        # If we want to do something in case of errors we'd do it here.
                print("Error removing role")
                pass
        else:
            try:
            # Finally, add the role.
                await interaction.user.add_roles(role)
            except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
                print("Error Adding Role")
                pass
        await interaction.response.send_message("Role updated.", ephemeral=True)
        

class aclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.synced = False

    # Need to move this far up.
    async def setup_hook(self) -> None:
            # Register the persistent view for listening here.
            # Note that this does not send the view to any message.
            # In order to do this you need to first send a message with the View, which is shown below.
            # If you have the message_id you can also pass it as a keyword argument, but for this example
            # we don't have one.
            self.add_view(Role_Buttons())
            self.persistent_views_added = True
        
client = aclient()
tree = app_commands.CommandTree(client)

intents = discord.Intents.all()
Intents.members = True

my_secret = os.getenv('Discord_Secret')

# Authentication with Twitch API.
client_id = os.getenv('twitch_id')
client_secret = os.getenv('twitch_secret')
body = {
    'client_id': client_id,
    'client_secret': client_secret,
    "grant_type": 'client_credentials'
}
r = requests.post('https://id.twitch.tv/oauth2/token', body)
keys = r.json()
headers = {
    'Client-ID': client_id,
    'Authorization': 'Bearer ' + keys['access_token']
}

GUILD_ID = guild= discord.Object(id= 980108559226380318)

# Twitter auth
twitclient = tweepy.Client(bearer_token=os.getenv('twit_bearer_token'),
                       consumer_key=os.getenv('twit_consumer_key'),
                       consumer_secret=os.getenv('twit_consumer_secret'),
                       access_token=os.getenv('twit_access_token'),
                       access_token_secret=os.getenv('twit_access_token_secret'))
twitclient.wait_on_rate_limit=True

start_time = datetime.now()


@client.event
async def on_disconnect():
    uptimedelta = datetime.now() - start_time
    print('ShowtimeRL Bot was disconnected at ' + datetime.ctime(start_time) + '. ShowtimeRL Bot has been up for ' + str(timedelta(seconds=uptimedelta.seconds)))

@client.event
async def on_resumed():
    uptimedelta = datetime.now() - start_time
    print("ShowtimeRL Bot reconnected " + datetime.ctime(start_time) + '. ShowtimeRL Bot has been up for ' + str(timedelta(seconds=uptimedelta.seconds)))

@client.event
async def on_connect():
    print('ShowtimeRL Bot was connected starting at ' + datetime.ctime(datetime.now()))

# Logs exception to .txt file.
def log_and_print_exception(e):
    logging_file = open("log.txt", "a")
    logging_file.write(f"{datetime.now()}\n{str(e)}\n\n")
    logging_file.close()
    print(f"Exception logged. Error:\n{e}")

# Gets a twitter account's latest tweet.
def checktwitter(twitter_name, self=None):
    user = twitclient.get_user(username=twitter_name) # Takes in plain text uername (id) and turns it into user information.
    tweets = twitclient.get_users_tweets(user.data.id, exclude='replies,retweets') # Takes the user information and turns it into a user id to be used for get_users_tweets. Then grabs the 10 latest tweets.
    mostrecenttweet = tweets.data[0].id
    return mostrecenttweet

# Returns true if online, false if not.
def checkuser(streamer_name, self=None):
    try:
        stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name,
                              headers=headers)
        if streamer_name is not None and str(stream) == '<Response [200]>':
            stream_data = stream.json()

            if len(stream_data['data']) == 1:
                return True, stream_data
            else:
                return False, stream_data
        else:
            stream_data = None
            return False, stream_data
    except Exception as e:
        self.log_and_print_exception(e)
        stream_data = None
        return False, stream_data

# Checks if the live notification has already been sent.
async def has_notif_already_sent(channel, twitch_name):
    async for message in channel.history(limit=200):
            if f"\nhttps://twitch.tv/{twitch_name}" in message.content:
                return message
    else:
        return False

# Checks if a tweet has already been sent
async def has_tweet_already_sent(channel, tweet_id):
    async for message in channel.history(limit=200):
            if f'https://vxtwitter.com/twitter/statuses/{tweet_id}' in message.content:
                return message
    else:
        return False

# 0=botlog, 1=tweets, 2=streams, 3=modmail, 4=announcements
def get_channel(id):
    file = open('channels.txt', "r")
    channels = file.read()
    channel_list = channels.split(",")
    try:
        request = channel_list[id]
    except:
        print("Channel not listed listed in channel file!")
    file.close()
    return request

# Function to convert 
def listToStringNewline(s):
   
    # initialize an empty string
    str1 = "\n"
   
    # return string 
    return (str1.join(s))

def listToString(s):
    str1 = ", "
    
    return (str1.join(s))

# Contains the live event loop.
@client.event
async def on_ready():
    await discord.Client.wait_until_ready(client)
    if not client.synced:
        await tree.sync(guild= GUILD_ID)
        self.synced = True
    print(f"Bot has logged in.")
    # Defines a loop that will run every 10 seconds (checks for live users every 10 seconds).

    @tasks.loop(seconds=60)
    async def live_notifs_loop():

        # Opens and reads the json file
        with open('tweeters.txt', 'r') as file2:
            tweeters = (file2.readline())
        
        tweeterlist = tweeters.split(",")
        
        with open('streams.txt', 'r') as file:
            streams = (file.readline())

        streamlist = streams.split(",")

        # Makes sure the json isn't empty before continuing.
        try:
            if tweeters != "":
                channel1 = client.get_channel(int(get_channel(1)))

                for twitter_name in tweeterlist:
                    if twitter_name == '':
                       break
                    tweet_id = checktwitter(twitter_name)
                    message = await has_tweet_already_sent(channel1, tweet_id)
                    if message is False:
                        print(f"{twitter_name} tweeted. Sending a notification.")
                        message = 'https://vxtwitter.com/twitter/statuses/'+str(tweet_id)
                        await channel1.send(message)
            if streams != "":
                # Gets the guild, 'twitch streams' channel, and streaming role.
                channel = client.get_channel(int(get_channel(2)))
                # Loops through the json and gets the key,value which in this case is the user_id and twitch_name of
                # every item in the json.
                for twitch_name in streamlist:
                    if twitch_name == '':
                        break
                    # Takes the given twitch_name and checks it using the checkuser function to see if they're live.
                    # Returns either true or false.
                    status, stream_data = checkuser(twitch_name)
                    # Makes sure they're live
                    if status is True:
                        # Checks to see if the live message has already been sent.
                        message = await has_notif_already_sent(channel, twitch_name)
                        if message is not False:
                            continue
                        await channel.send(
                            f":red_circle: **LIVE**"
                            f"\n@here Come watch!"
                            f"\n{stream_data['data'][0]['title']}"
                            f"\nhttps://twitch.tv/{twitch_name}")
                        print(f"A livestream has started. Sending a notification.")
                        continue
                    # If they aren't live do this:
                    elif stream_data is not None:
                        # Checks to see if the live notification was sent.
                        message = await has_notif_already_sent(channel, twitch_name)
                        if message is not False:
                            print(f"A livestream has stopped. Removing the notification.")
                            await message.delete()
        except TypeError as e:
            log_and_print_exception(e)
            raise e
        file.close()

    # Start your loop.
    live_notifs_loop.start()

class ModMailModal(ui.Modal, title='Mod Mail'):
    Title = discord.ui.TextInput(label='Title', required=True, style=discord.TextStyle.short)
    Mail = discord.ui.TextInput(label= "Message", default= "Write what you want sent here.", required=True, style=discord.TextStyle.paragraph)
    Notes = discord.ui.TextInput(label= "Additional Notes", default="\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b\u200b", style=discord.TextStyle.short, required=False)
    # Notes fix is definitely a band-aid. Can't find a way to let Notes just be empty without these dumb empty space characters
    async def on_submit(self, interaction):
        channel = client.get_channel(int(get_channel(3)))
        author = interaction.user
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"Mod Mail from {author}",)
        try:
            embed.set_thumbnail(url=f"{author.avatar.url}")
        except:
            embed.set_thumbnail(url='https://styles.redditmedia.com/t5_2qhk5/styles/communityIcon_v58lvj23zo551.jpg')
            print(f'{author} did not have an avatar url.')
        embed.add_field(name="**Title**", value=f"{self.Title}", inline=False)
        embed.add_field(name=f"**Mail Content**", value=f"{self.Mail}", inline=False)
        embed.add_field(name=f"**Additional Notes**", value=f"{self.Notes}", inline=False)
        embed.timestamp = datetime.now()
        await interaction.response.send_message("Your Mod Mail has been recorded and sent as follows.",embed=embed)
        await channel.send(embed=embed)

# This is caled when the bot is DM'd. It displays buttons for the user.
class DM_Help(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='❓', style=discord.ButtonStyle.gray)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("This will become helpful info!")
        self.value = "❓"
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='💬', style=discord.ButtonStyle.blurple)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        x = ModMailModal()
        await interaction.response.send_modal(x)
        await TeamModal.wait(x)
        self.value = "💬"
        self.stop()

# This bit of code has the bot respond to DMs automatically, should be turned into a helpful message eventually.
@client.event
async def on_message(message):
    channel = client.get_channel(int(get_channel(3)))
    if message.author == client.user:
        return 
    if not message.guild:
        try:
            view= DM_Help()

            await message.channel.send("Hi, how can I help you?\n❓ : Command list\n💬 : Mod Mail\n", view=view)
            await view.wait()
            # If you want to add something to this then check the DM_Help class.
        except discord.errors.Forbidden:
            pass
    else:
        pass

# This command lets you add a twitter account to the notification list.
@tree.command(name="twitter_add", description=f'Adds a Twitter to the live notifs.', guild= GUILD_ID)
async def self(interaction: discord.Interaction, twitter_name: str):
    id = int(get_channel(0))
    channel = client.get_channel(id)
    # Opens and reads the json file.
    with open('tweeters.txt', 'a') as file:

    # Assigns their given twitch_name to their discord id and adds it to the streamers.json.
        file.writelines(f'{twitter_name},')

    # Tells the user it worked.
        await interaction.response.send_message(f"Added {twitter_name} to the notifications list.")
        await channel.send (f"{twitter_name} was added to the notification list by {interaction.user.mention}.")
        print(f"Added {twitter_name} to the notifications list.")
    file.close()

# This command lets you remove a twitter account from the notification list.
@tree.command(name="twitter_delete", description=f'Removes a Twitter from the live notifs.', guild= GUILD_ID)
async def self(interaction: discord.Interaction, twitter_name: str):
    channel = client.get_channel(int(get_channel(1)))
    channel2 = client.get_channel(int(get_channel(0)))
    # Opens and reads the json file.
    try:
        with open('tweeters.txt', 'r') as file:
            tweeters = (file.read())
            tweeterlist = tweeters.split(",")
            tweeterlist.remove(f'{twitter_name}')
            newtweeters = ",".join(tweeterlist)
            #print(newtweeters)
            message = await has_notif_already_sent(channel, twitter_name)
            if message is not False:
                print(f"A tweeter was removed. Removing the notification. Is this needed?")
                await message.delete()
        file.close()
        # Adds the changes we made to the json file.
        with open('tweeters.txt', 'w') as file:
            file.writelines(newtweeters)
            file.close()
        # Tells the user it worked.
            await interaction.response.send_message(f"Removed {twitter_name} from the notifications list.")
            await channel2.send(f"{twitter_name} was removed from the notification list by {interaction.user.mention}.")
            print(f"Removed {twitter_name} from the notifications list.")
    except:
        await interaction.response.send_message(f"Error Occurred.")
    file.close()

# This command lists twitter accounts currently within the notification list.
@tree.command(name="twitter_list", description=f'List of twitters currently being tracked.', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
     with open('tweeters.txt', 'r') as file:
         tweeters = file.read()
         await interaction.response.send_message(f'The currently tracked streams include: {tweeters}')
         file.close()

# This command lets you add a streamer to the notification list.
@tree.command(name="stream_add", description=f'Adds a Twitch to the live notifs.', guild= GUILD_ID)
async def self(interaction: discord.Interaction, twitch_name: str):
    id = int(get_channel(0))
    channel = client.get_channel(id)
    # Opens and reads the json file.
    with open('streams.txt', 'a') as file:

    # Assigns their given twitch_name to their discord id and adds it to the streamers.json.
        file.writelines(f'{twitch_name},')

    # Tells the user it worked.
        await interaction.response.send_message(f"Added {twitch_name} to the notifications list.")
        await channel.send (f"{twitch_name} was added to the notification list by {interaction.user.mention}.")
        print(f"Added {twitch_name} to the notifications list.")
    file.close()

# This command lets you remove a streamer from the notification list.
@tree.command(name="stream_delete", description=f'Removes a Twitch from the live notifs.', guild= GUILD_ID)
async def self(interaction: discord.Interaction, twitch_name: str):
    channel = client.get_channel(int(get_channel(2)))
    channel2 = client.get_channel(int(get_channel(0)))
    # Opens and reads the json file.
    try:
        with open('streams.txt', 'r') as file:
            streams = (file.read())
            streamlist = streams.split(",")
            streamlist.remove(f'{twitch_name}')
            newstreams = ",".join(streamlist)
            #print(newstreams)
            message = await has_notif_already_sent(channel, twitch_name)
            if message is not False:
                print(f"A livestream has stopped. Removing the notification.")
                await message.delete()
        file.close()
        # Adds the changes we made to the json file.
        with open('streams.txt', 'w') as file:
            file.writelines(newstreams)
            file.close()
        # Tells the user it worked.
            await interaction.response.send_message(f"Removed {twitch_name} from the notifications list.")
            await channel2.send(f"{twitch_name} was removed from the notification list by {interaction.user.mention}.")
            print(f"Removed {twitch_name} from the notifications list.")
    except:
        await interaction.response.send_message(f"Error Occurred.")
    file.close()

# This command lists streamers currently within the notification list.
@tree.command(name="stream_list", description=f'List of streams currently being tracked.', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
     with open('streams.txt', 'r') as file:
         streams = file.read()
         await interaction.response.send_message(f'The currently tracked streams include: {streams}')
         file.close()

# Used in conjunction with the /setchannel command. This actually changes the channel.
async def change_channel(self, chosen_channel):
    with open('temp_function.txt', 'r') as file:
        chosen_function = file.read()
    file.close()
        
    if chosen_function == "Bot Log":
        chosen_function = 0
    elif chosen_function == "Tweet Channel":
        chosen_function = 1
    elif chosen_function == "Stream Channel":
        chosen_function = 2
    elif chosen_function == "Mod Mail":
        chosen_function = 3
    elif chosen_function == "Announcement Channel":
        chosen_function = 4
        
    with open('channels.txt', 'r') as file:
        channels = file.read()
        channel_list = channels.split(',')
        channel_list[int(chosen_function)] = str(chosen_channel)
        newchannels = ",".join(channel_list)
        file.close()
    with open('channels.txt', "w") as file:
        file.writelines(newchannels)
        file.close()
    
# Used in /setchannel, has the info for the channel select dropdown.
class ChannelDropdown(discord.ui.Select):
    def __init__(self):
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_name_list.append(channel.name)
                    text_channel_id_list.append(channel.id)
        options = [
            discord.SelectOption(label=key)
            for key in text_channel_name_list
        ]
        super().__init__(placeholder='Choose a channel..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_id_list.append(channel.id)
                    text_channel_name_list.append(channel.name)
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        
        id = text_channel_id_list[text_channel_name_list.index(self.values[0])]
        await change_channel(self, id)
        await interaction.response.send_message(f"You chose <#{id}>\nThe Bot is now updated.")
        
        botid = int(get_channel(0))
        botchannel = client.get_channel(botid)
        
        with open('temp_function.txt', 'r') as file:
            chosen_function = file.read()
        file.close()
        
        await botchannel.send(f"{interaction.user.mention} changed the {chosen_function} to <#{id}>")
        
# Used in /setchannel, has the info for the function select dropdown.
class FunctionDropdown(discord.ui.Select):
    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Bot Log', emoji='⬛'),
            discord.SelectOption(label='Tweet Channel', emoji='🟦'),
            discord.SelectOption(label='Stream Channel', emoji='🟪'),
            discord.SelectOption(label='Mod Mail', emoji='🟥'),
            discord.SelectOption(label="Announcement Channel", emoji='⬜')
        ]
        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose a function..', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        view = ChannelDropdownView()
        with open('temp_function.txt', 'w') as file:
            file.writelines(self.values[0])
        file.close()
        
        await interaction.response.send_message(f"You chose the **{self.values[0]}** function.\nNow choose which channel you'd like to attach it to.", view=view)

# Creates the view for the Function Dropdown.
class FunctionDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FunctionDropdown())

# Creates the view for the Channel Dropdown.
class ChannelDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(ChannelDropdown())

# Replaces the old set commands and combines them into 1 elegant solution.
@tree.command(name="setchannel", description="Lets you set various channels.", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    view = FunctionDropdownView()
    await interaction.response.send_message('Choose a function to change.', view=view)

# Lists channels the bot is outputting too.
@tree.command(name="mod_channel_list", description=f"Display all bot configured channels", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f"The current channels are:\nBot Log: <#{int(get_channel(0))}>\nTweet Channel: <#{int(get_channel(1))}>\nStream Channel: <#{int(get_channel(2))}>\nMod-Mail Channel: <#{int(get_channel(3))}>\nAnnouncement Channel: <#{int(get_channel(4))}>")

# Used in /announce, contains the dropdown to select the proper channel.
class AnnounceDropdown(discord.ui.Select):
    def __init__(self):
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_name_list.append(channel.name)
                    text_channel_id_list.append(channel.id)
        options = [
            discord.SelectOption(label=key)
            for key in text_channel_name_list
        ]
        super().__init__(placeholder='Choose a channel..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_id_list.append(channel.id)
                    text_channel_name_list.append(channel.name)
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        
        id = text_channel_id_list[text_channel_name_list.index(self.values[0])]
        Announcement_Channel = client.get_channel(id)
        BotLog = client.get_channel(int(get_channel(0)))
        
        with open('temp_announcement.txt', 'r') as file:
            announcement = file.read()
        file.close()
        await interaction.response.send_message("Your message has been sent!", ephemeral=True)
        await BotLog.send(f'{interaction.user.mention} sent the message "{announcement}" using the bot in <#{id}>')
        await Announcement_Channel.send(f"{announcement}")
        
# Creates the view for the Announce Dropdown.
class AnnounceDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(AnnounceDropdown())

# Lets the user say things through the bot in a specified channel.
@tree.command(name="say", description=f'Sends a message to the specified channel as the bot.', guild= GUILD_ID)
async def self(interaction: discord.Interaction, message: str):
    view= AnnounceDropdownView()
    with open('temp_announcement.txt', 'w') as file:
        file.writelines(message)
    file.close()
        
    await interaction.response.send_message("What channel would you like to send an announcement to?", view=view)
    
# Future help command!
@tree.command(name="help", description=f'Sends the User a DM with command information.', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    user = interaction.user
    print(f'Sent a help message to {user}')
    await interaction.response.send_message("A DM has been sent!", ephemeral = True)
    embed = discord.Embed(
            color=discord.Color.random(),
            title=f"Command List")
    #embed.add_field(name="announce", value="Lets you")
    embed.add_field(name="hello", value='The bot will respond back with a simple "Hello @you!"', inline=False)
    embed.add_field(name="help", value="Sends this message.", inline = False)
    embed.add_field(name="ping", value='Checks the latency of the bot. Responds with "Pong! **ms"', inline=False)
    #embed.add_field(name="", value="")

    embed.timestamp = datetime.now()
    await user.send(embed=embed)
    
# Pong!
@tree.command(name="ping", description=f'Reports latency.', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong! {round(client.latency * 1000)}ms')

# Friendly bot :)
@tree.command(name="hello", description=f'Has the bot say Hi', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    author = interaction.user
    await interaction.response.send_message(f'Hello {author.mention}!')

# Sends information to the bot log about any user who joins.
@client.event
async def on_member_join(member):
    botlog = client.get_channel(int(get_channel(0)))
    guildname = client.fetch_guild.__name__
    await member.send(f'Welcome to {guildname} {member.mention}!')
    try:
        roles = [role for role in member.roles[1:]]
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"{member}",
            description=f"{member.mention}")
        embed.add_field(name="**ID**", value=f"{member.id}", inline=True)
        try:
            embed.set_thumbnail(url=f"{member.avatar.url}")
        except:
            embed.set_thumbnail(url='https://styles.redditmedia.com/t5_2qhk5/styles/communityIcon_v58lvj23zo551.jpg')
            print(f'{member} did not have an avatar url.')
        embed.add_field(name=f"**Roles ({len(member.roles) - 1})**",
                         value=' • '.join([role.mention for role in roles]), inline=False)
        embed.add_field(name="**Account Creation Date **", value=f"{member.created_at}".replace("-", "/"),
                        inline=True)
        embed.add_field(name="**Server Join Date**", value=f"{member.joined_at}".replace("-", "/"),
                        inline=True)
        embed.timestamp = datetime.now()
        await botlog.send(embed=embed)
    except:
        roles = [role for role in member.roles[1:]]
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"{member}",
            description=f"{member.mention}")
        embed.add_field(name="**ID**", value=f"{member.id}", inline=True)
        try:
            embed.set_thumbnail(url=f"{member.avatar.url}")
        except:
            embed.set_thumbnail(url='https://styles.redditmedia.com/t5_2qhk5/styles/communityIcon_v58lvj23zo551.jpg')
            print(f'{member} did not have an avatar url.')
        embed.add_field(name=f"**Roles (0)**", value="No roles", inline=False)
        embed.add_field(name="**Account Creation Date **", value=f"{member.created_at}".replace("-", "/"),
                        inline=True)
        embed.add_field(name="**Server Join Date**", value=f"{member.joined_at}".replace("-", "/"),
                        inline=True)
        embed.timestamp = datetime.now()
        await botlog.send(embed=embed)
    await client.wait_until_ready()

# Modal for showmatch test, sends info to Matches.txt
class TeamModal(ui.Modal, title='Team Information'):
    TeamName = discord.ui.TextInput(label='Team Name', required=True)
    Players = discord.ui.TextInput(label= "Player IDs", default= "Master Nox#6330, Master Nox#6330, Master Nox#6330", required=True)
    #Player1 = discord.ui.TextInput(label= "Player 1 ID", default= "Master Nox#6330", required=True)
    #Player2 = discord.ui.TextInput(label= "Player 2 ID", default= "BluBlazing#7777", required=True)
    #Player3 = discord.ui.TextInput(label= "Player 3 ID", default= "Planet#9951", required=True)
    Subs = discord.ui.TextInput(label= "Sub IDs", default= "BluBlazing#7777, BluBlazing#7777, BluBlazing#7777", required=True)
    #Subs = discord.ui.Select(options=[discord.SelectOption(label='Yes Subs'), discord.SelectOption(label='No Subs')])
    RankInfo = discord.ui.TextInput(label="Average Team Rank", default="0", required=True)
    
    async def on_submit(self, interaction):
        author = interaction.user
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"Match Request from {author}",
            description=f"You've received a match request!\nPlease accept or deny after checking the details.")
        try:
            embed.set_thumbnail(url=f"{author.avatar.url}")
        except:
            embed.set_thumbnail(url='https://styles.redditmedia.com/t5_2qhk5/styles/communityIcon_v58lvj23zo551.jpg')
            print(f'{author} did not have an avatar url.')
        embed.add_field(name="**Team Name**", value=f"{self.TeamName}", inline=False)
        embed.add_field(name=f"**Players**", value=f"{self.Players}", inline=True)
        embed.add_field(name=f"**Subs**", value=f"{self.Subs}", inline=True)
        embed.add_field(name="**Average Rank**", value=f"{self.RankInfo}", inline=False)
        embed.timestamp = datetime.now()
        
        with open(f'./Matches.txt', 'a') as file:
            file.writelines(f'{datetime.now()}, {self.TeamName}, {self.Players}, {self.Subs}, {self.RankInfo}\n')
        file.close()
        
        await interaction.response.send_message("Your information has been recorded and sent as follows.",embed=embed, ephemeral=True)

class ConfirmDeny(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='✔️', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You've accepted the match!")
        self.value = "✔️"
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='❌', style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You've denied the match!")
        self.value = "❌"
        self.stop()

class ConfirmDenyDeletion(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='✔️', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = "✔️"
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='❌', style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = "❌"
        self.stop()

# Test for the showmatch system. Need to find a way to properly record and remember information.
@tree.command(name="showmatch_test", description=f'WIP', guild= GUILD_ID)
async def self(interaction: discord.Interaction, usertag: str):
    author = interaction.user
    user = usertag.removeprefix('<@!')
    user = user.removesuffix('>')
    user = int(user)
    user = await client.fetch_user(user)
    x = TeamModal()
    await interaction.response.send_modal(x)
    await TeamModal.wait(x)
    TeamName1 = x.children[0].view.TeamName.value
    Team1Players = x.children[0].view.Players.value
    Team1Subs = x.children[0].view.Subs.value
    Team1Rank = x.children[0].view.RankInfo.value
    embed = discord.Embed(
            color=discord.Color.random(),
            title=f"Match Request from {author}",
            description=f"You've received a match request!\nPlease accept or deny after checking the details.")
    try:
        embed.set_thumbnail(url=f"{author.avatar.url}")
    except:
        embed.set_thumbnail(url='https://styles.redditmedia.com/t5_2qhk5/styles/communityIcon_v58lvj23zo551.jpg')
        print(f'{author} did not have an avatar url.')
    embed.add_field(name="**Team Name**", value=f"{TeamName1}", inline=False)
    embed.add_field(name=f"**Players**", value=f"{Team1Players}", inline=True)
    embed.add_field(name=f"**Subs**", value=f"{Team1Subs}", inline=True)
    embed.add_field(name="**Average Rank**", value=f"{Team1Rank}", inline=False)
    embed.timestamp = datetime.now()
    view = ConfirmDeny()
    await user.send(embed=embed, view=view)
    await ConfirmDeny.wait(view)
    conn = http.client.HTTPSConnection('eor82olfyhrllj.m.pipedream.net')
    conn.request("POST", "/", '{"Information": "'+TeamName1+'"}', {'Content-Type': 'application/json'})
    if view.children[0].view.confirm.view.value == "✔️":
        await author.send(f"Your opponent ({usertag}) has accepted the match!")
    else:
        await author.send(f"Your opponent ({usertag}) has denied the match!")

# Modal to gather team information.
class TeamModal2(ui.Modal, title='Team Information'):
    TeamName = discord.ui.TextInput(label='Team Name', required=True)
    Players = discord.ui.TextInput(label= "Player IDs", default= "Master Nox#6330, Master Nox#6330, Master Nox#6330", required=True)
    Subs = discord.ui.TextInput(label= "Sub IDs", default= "BluBlazing#7777, BluBlazing#7777, BluBlazing#7777", required=True)
    RankInfo = discord.ui.TextInput(label="Average Team Rank", default="0", required=True)
    
    async def on_submit(self, interaction):
        # author = interaction.user
        # embed = discord.Embed(
        #     color=discord.Color.random(),
        #     title=f"Match Request from {author}",
        #     description=f"You've received a match request!\nPlease accept or deny after checking the details.")
        # try:
        #     embed.set_thumbnail(url=f"{author.avatar.url}")
        # except:
        #     embed.set_thumbnail(url='https://styles.redditmedia.com/t5_2qhk5/styles/communityIcon_v58lvj23zo551.jpg')
        #     print(f'{author} did not have an avatar url.')
        # embed.add_field(name="**Team Name**", value=f"{self.TeamName}", inline=False)
        # embed.add_field(name=f"**Players**", value=f"{self.Players}", inline=True)
        # embed.add_field(name=f"**Subs**", value=f"{self.Subs}", inline=True)
        # embed.add_field(name="**Average Rank**", value=f"{self.RankInfo}", inline=False)
        # embed.timestamp = datetime.now()
        
        # with open(f'./Matches.txt', 'a') as file:
        #     file.writelines(f'{datetime.now()}, {self.TeamName}, {self.Players}, {self.Subs}, {self.RankInfo}\n')
        # file.close
        
        await interaction.response.send_message("Please enter your team information.", ephemeral=True)

# Modal class to edit already existing team info.
class TeamInfoEdit(ui.Modal, title='Edit Team Information'):
    TeamName = discord.ui.TextInput(label='Team Name', required=True)
    Players = discord.ui.TextInput(label= "Player IDs", default= "Master Nox#6330, Master Nox#6330, Master Nox#6330", required=True)
    Subs = discord.ui.TextInput(label= "Sub IDs", default= "BluBlazing#7777, BluBlazing#7777, BluBlazing#7777", required=True)
    RankInfo = discord.ui.TextInput(label="Average Team Rank", default="0", required=True)
    
    async def on_submit(self, interaction):
        
        with open('temp_teams_list.txt', 'r') as file:
            team = file.read()
        file.close()
                
        with open('temp_author.txt', 'r') as file:
            authordata = file.readlines()
        file.close()
        index = -2
        
        author = authordata[0]
        authorid = authordata[1]
        
        with open('Teams.txt', 'r') as file:
            data = file.readlines()
        file.close()
        
        with open('Teams.txt', 'r') as file:
            for line in file:
                index +=1
                if line == f'Team Name: {team}\n':
                    break
        file.close()
        
        data[index] = f'Captain: {author}\n'
        data[index] = f'Captain ID: {authorid}\n'
        data[index+1] = f'Team Name: {self.children[0].view.TeamName}\n'
        data[index+2] = f'Team Players: {self.children[0].view.Players}\n'
        data[index+3] = f'Team Subs: {self.children[0].view.Subs}\n'
        data[index+4] = f'Average Team Rank: {self.children[0].view.RankInfo}\n'
        
        with open(f'Teams.txt', 'w') as file:
            file.writelines(data)
        file.close()
        
        await interaction.response.send_message(f"Team **{self.children[0].view.TeamName}** has been updated.", ephemeral=True)

# Attatchement Class.
class TeamEditView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(TeamEditView2())

# Dropdown view for teams that the author is the Captain of.
class TeamEditView2(discord.ui.Select):
    def __init__(self):
        Teams = []
        with open('temp_teams_list.txt', 'r') as file:
            for line in file:
                Team = line.rstrip()

                Teams.append(Team)
        file.close()
        options = [
            discord.SelectOption(label=key)
            for key in Teams
        ]
        super().__init__(placeholder='Choose a team..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        with open('temp_teams_list.txt', 'w') as file:
            file.write(f'{self.values[0]}')
        file.close()
                
        x = TeamInfoEdit()
        await interaction.response.send_modal(x)
        await TeamInfoEdit.wait(x)

# Attatchement Class.
class MatchView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(MatchView2())

# Dropdown view for teams that the author is the Captain of.
class MatchView2(discord.ui.Select):
    def __init__(self):
        Teams = []
        with open('temp_teams_list.txt', 'r') as file:
            for line in file:
                Team = line.rstrip()

                Teams.append(Team)
        file.close()
        options = [
            discord.SelectOption(label=key)
            for key in Teams
        ]
        super().__init__(placeholder='Choose a team..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        with open('temp_match_request.txt', 'w') as file:
            file.write(f'{self.values[0]}')
        file.close()
        
        with open('temp_author.txt', 'r') as file:
            authordata = file.readlines()
        file.close()
        
        author = authordata[0]
        authorid = int(authordata[1])
        
        Teams = []
        flag2 = 0

        with open('Teams.txt', 'r') as file:
            for line in file:
                if line.startswith("Captain ID: "):
                    if f"{authorid}" in line:
                        flag2 = 0
                    else:
                        flag2 = 1
                if flag2 == 1:
                    TeamName = str(file.readline())
                    TeamName = TeamName.replace("Team Name: ", "")
                    TeamName = TeamName.rstrip("\n")
                    Teams.append(TeamName)
                    flag2 = 0
        file.close()
                
        Teams = listToStringNewline(Teams)
        
        with open('temp_match_request2.txt', 'w') as file:
            file.writelines(Teams)
        file.close()
        
        view = OpponentMatchView()
        
        await interaction.response.send_message(f"Choose an opponent...", view= view, ephemeral=True)


class OpponentMatchView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(OpponentMatchView2())


class OpponentMatchView2(discord.ui.Select):
    def __init__(self):
        Teams = []
        with open('temp_match_request2.txt', 'r') as file:
            for line in file:
                Team = line.rstrip()

                Teams.append(Team)
        file.close()
        options = [
            discord.SelectOption(label=key)
            for key in Teams
        ]
        super().__init__(placeholder='Choose a team..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        
        
        index = 0
        
        with open('temp_author.txt', 'r') as file:
            authordata = file.readlines()
        file.close()
        
        author = authordata[0]
        authorid = int(authordata[1])
        
        with open('Teams.txt', 'r') as file:
            data = file.readlines()
        file.close()
        
        with open('temp_match_request.txt', 'r') as file:
            TeamtoSend = file.read()
        file.close()
        
        with open('Teams.txt', 'r') as file:
            for line in file:
                index +=1
                if line == f'Team Name: {TeamtoSend}\n':
                    break
        file.close()
        
        index2 = 0
        with open('Teams.txt', 'r') as file:
            for line in file:
                index2 +=1
                if line == f'Team Name: {self.values[0]}\n':
                    break
        file.close()
        
        Captain = data[index2-2]
        Captain = Captain.replace("Captain ID: ", "")
        Captain = Captain.rstrip()
        
        Captain = await client.fetch_user(int(Captain))
        Author = await client.fetch_user(authorid)
        
        TeamName = data[index-1]
        TeamName = TeamName.replace("Team Name: ", "")
        
        TeamPlayers = data[index]
        TeamPlayers = TeamPlayers.replace("Team Players: ", "")
        
        TeamSubs = data[index+1]
        TeamSubs = TeamSubs.replace("Team Subs: ", "")
        
        TeamRank = data[index+2]
        TeamRank = TeamRank.replace("Average Team Rank: ", "")
        
        embed = discord.Embed(
                color=discord.Color.random(),
                title=f"Match Request from {Author}",
                description=f"You've received a match request!\nPlease accept or deny after checking the details.")
        try:
            embed.set_thumbnail(url=f"{Author.avatar.url}")
        except:
            embed.set_thumbnail(url='https://styles.redditmedia.com/t5_2qhk5/styles/communityIcon_v58lvj23zo551.jpg')
            #print(f'{Author} did not have an avatar url.')
        embed.add_field(name="**Team Name**", value=f"{TeamName}", inline=False)
        embed.add_field(name=f"**Players**", value=f"{TeamPlayers}", inline=True)
        embed.add_field(name=f"**Subs**", value=f"{TeamSubs}", inline=True)
        embed.add_field(name="**Average Rank**", value=f"{TeamRank}", inline=False)
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(f"Your match request has been sent to the captain of **{self.values[0]}**.", ephemeral=True)
        
        view = ConfirmDeny()
        await Captain.send(embed=embed, view=view)
        await ConfirmDeny.wait(view)
        
        Title = TeamName + " VS. " + str(self.values[0])
        Date = '2022-07-08'
        
        # body = {
        #     "Title": Title,
        #     "Date": Date
        # }
        
        # conn = http.client.HTTPSConnection('eor82olfyhrllj.m.pipedream.net')
        # #conn.request("POST", "/", '{"Title": "'+Title+'"}', {'Content-Type': 'application/json'})
        # conn.request({'Content-Type': 'multipart/form-data'}, url="/", body= body)
        
        payload = { 'Title': Title,
            'Date': Date}
        session = requests.Session()
        session.post('https://eor82olfyhrllj.m.pipedream.net',data=payload)

        
        
        if view.children[0].view.confirm.view.value == "✔️":
            await Author.send(f"Your opponent {Captain} has accepted the match!")
        else:
            await Author.send(f"Your opponent {Captain} has denied the match!")
                
class DeleteTeamView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(DeleteTeamView2())

# Dropdown view for teams that the author is the Captain of.
class DeleteTeamView2(discord.ui.Select):
    def __init__(self):
        Teams = []
        with open('temp_teams_list.txt', 'r') as file:
            for line in file:
                Team = line.rstrip()

                Teams.append(Team)
        file.close()
        options = [
            discord.SelectOption(label=key)
            for key in Teams
        ]
        super().__init__(placeholder='Choose a team to delete..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        with open('temp_author.txt', 'r') as file:
            authordata = file.readlines()
        file.close()
        
        authorid = authordata[1]
        
        Captain = await client.fetch_user(int(authorid))
        
        
        
        view = ConfirmDenyDeletion()
        await interaction.response.send_message(f"Please confirm in DM's.", ephemeral=True)
        await Captain.send(f'Are you certain you want to delete team **{self.values[0]}**?', view=view)
        await ConfirmDenyDeletion.wait(view)
        
        if view.children[0].view.confirm.view.value == "✔️":
            # Now actually delete the info lol
            index = 0
            flag = 0
            
            with open('Teams.txt', 'r') as file:
                data = file.readlines()
            file.close()
            
            with open('Teams.txt', 'r') as file:
                for line in file:
                    index +=1
                    if line == f'Team Name: {self.values[0]}\n':
                        flag = 1
                        break
            file.close()
            
            if data[index-2] == f'Captain ID: {authorid}\n' and flag == 1:
                data[index-3] = ""
                data[index-2] = ""
                data[index-1] = ""
                data[index] = ""
                data[index+1] = ""
                data[index+2] = ""
                data[index+3] = ""

                with open('Teams.txt', 'w') as file:
                    file.writelines(data)
                file.close()
                await Captain.send(f"Team **{self.values[0]}** has been deleted.")
            else:
                await Captain.send('Something went wrong. Contact Master Nox#6330 if the problem persists.')
        else:
            await Captain.send(f"Deletion cancelled.")
        

@tree.command(name="match_request", description="Updated Showmatch.", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    author = interaction.user
    with open('temp_author.txt', 'w') as file:
        file.write(str(author))
        file.write(f'\n{author.id}')
    file.close()
    
    Teams = []
    flag = 0
    flag2 = 0
    index = 0
    with open('Teams.txt', 'r') as file:
        for line in file:
            index +=1
            if "Captain ID: "+ str(author.id) in line:
                flag = 1
                flag2 = 1
            if flag2 == 1:
                TeamName = str(file.readline())
                TeamName = TeamName.replace("Team Name: ", "")
                TeamName = TeamName.rstrip("\n")
                Teams.append(TeamName)
                flag2 = 0
    file.close()
    with open('temp_teams_list.txt', 'w') as file:
        for Team in Teams:
            file.write(f"{Team}\n")
    file.close()
    
    view = MatchView()
    
    if flag == 0:
        await interaction.response.send_message("You are not listed as a captain for any of the teams in our database.", ephemeral=True)
    elif flag == 1:
        await interaction.response.send_message("Please select your team.", view = view, ephemeral=True)
     
@tree.command(name="edit_team", guild= GUILD_ID)
async def self(interaction:discord.Interaction):
    author = interaction.user
    authorid = author.id
    with open('temp_author.txt', 'w') as file:
        file.write(str(author))
        file.write(f'\n{authorid}')
    file.close()
    
    channel = interaction.channel
    Teams = []
    flag = 0
    flag2 = 0
    index = 0
    with open('Teams.txt', 'r') as file:
        for line in file:
            index +=1
            if "Captain: "+ str(author) in line:
                flag = 1
                flag2 = 1
            if flag2 == 2:
                TeamName = str(file.readline())
                TeamName = TeamName.replace("Team Name: ", "")
                TeamName = TeamName.rstrip("\n")
                Teams.append(TeamName)
                flag2 = 0
            if flag2 == 1:
                flag2 = 2
    file.close()
    with open('temp_teams_list.txt', 'w') as file:
        for Team in Teams:
            file.write(f"{Team}\n")
    file.close()
    if flag == 0:
        await interaction.response.send_message("You are not listed as a captain for any of the teams in our database.", ephemeral=True)
    elif flag == 1:
        await interaction.response.send_message("Please select the team you'd lke to edit.", view = TeamEditView(), ephemeral=True)
    
@tree.command(name="create_team", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    TeamCaptain = interaction.user
    CaptainID = TeamCaptain.id
    channel = interaction.channel
    x = TeamModal2()
    await interaction.response.send_modal(x)
    await TeamModal2.wait(x)
    TeamName = x.children[0].view.TeamName.value
    TeamPlayers = x.children[0].view.Players.value
    TeamSubs = x.children[0].view.Subs.value
    TeamRank = x.children[0].view.RankInfo.value
    
    index = 0
    flag = 0
    flag2 = 0
    with open('Teams.txt', 'r') as file:
        for line in file:
            index +=1
            if "Captain: "+ str(TeamCaptain) in line:
                flag = 1
            elif "Team Name: "+ TeamName in line:
                flag2 = 1
    file.close()
    if flag == 1 and flag2 == 1:
        await interaction.response.send_message(f"You are already listed as the Captain for **{TeamName}** in our database, consider /edit_team instead.", ephemeral=True)
    else:
        with open('Teams.txt', 'a') as file:
            file.writelines(f"Captain: {TeamCaptain}\nCaptain ID: {CaptainID}\nTeam Name: {TeamName}\nTeam Players: {TeamPlayers}\nTeam Subs: {TeamSubs}\nAverage Team Rank: {TeamRank}\n\n")
        file.close()
        await interaction.followup.send(f"Info for **{TeamName}** has been recorded.", ephemeral=True)
    
@tree.command(name='delete_team', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    TeamCaptain = interaction.user
    CaptainID = TeamCaptain.id
    
    with open('temp_author.txt', 'w') as file:
        file.write(str(TeamCaptain))
        file.write(f'\n{CaptainID}')
    file.close()
    
    Teams = []
    flag = 0
    flag2 = 0
    index = 0
    with open('Teams.txt', 'r') as file:
        for line in file:
            index +=1
            if "Captain ID: "+ str(CaptainID) in line:
                flag = 1
                flag2 = 1
            if flag2 == 1:
                TeamName = str(file.readline())
                TeamName = TeamName.replace("Team Name: ", "")
                TeamName = TeamName.rstrip("\n")
                Teams.append(TeamName)
                flag2 = 0
    file.close()
    with open('temp_teams_list.txt', 'w') as file:
        for Team in Teams:
            file.write(f"{Team}\n")
    file.close()
    
    view = DeleteTeamView()
    
    if flag == 0:
        await interaction.response.send_message("You are not listed as a captain for any of the teams in our database.", ephemeral=True)
    elif flag == 1:
        await interaction.response.send_message("Please select the team you wish to delete.", view = view, ephemeral=True)
    
@tree.command(name="role_test", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    view = Role_Buttons()
    await interaction.response.send_message("Test Role Message!", view=view)




    # This one is similar to the confirmation button except sets the inner value to `False`
    
    # @discord.ui.button(label='💬', style=discord.ButtonStyle.blurple)
    # async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     x = ModMailModal()
    #     await interaction.response.send_modal(x)
    #     await TeamModal.wait(x)
    #     self.value = "💬"
    #     self.stop()

    
# def getJson(username):
#   key = '8f8782a3-53e3-4174-bdf6-9d4329ce0f72' # Your key goes here, this is mine
#   platform = 'epic'
#   link = f"https://public-api.tracker.gg/v2/rocket-league/standard/profile/{platform}/{username}"
#   headers = {
#     'TRN-Api-Key' : key,
#   }
#   response = requests.get(link, headers=headers)
#   jsonResponse = json.loads(response.text)
#   return jsonResponse
#
# def getSummary(username):
#   jsonResponse = getJson(username)
#   stuff = {}
#   for x in range(10):
#     try: stuff[jsonResponse['data']['segments'][x]['metadata']['name']] = jsonResponse['data']['segments'][x]['stats']['tier']['metadata']['name']
#     except:
#         None
#   return stuff

#@client.command(aliases = ['rank'])
# async def Rank(ctx, username, mode):
#     print(username)
#     print(mode)
#     jsonResponse = getSummary(username)
#     translation = {'1': 'Ranked Duel 1v1', '2': 'Ranked Doubles 2v2', '3': 'Ranked Standard 3v3', 'hoops': 'Hoops',
#                    'rumble': 'Rumble', 'dropshot': 'Dropshot', 'snowday': 'Snowday', 'tournament': 'Tournament Matches',
#                    'unranked': 'Un-Ranked'}
#     return jsonResponse[translation[mode.lower()]]

client.run(my_secret)