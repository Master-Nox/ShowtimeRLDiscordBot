from __future__ import print_function
from cProfile import label
from email import message
from errno import EPERM
import json
from msilib.schema import File, TextStyle
from socket import timeout
from tkinter import Button
import requests
from requests_oauthlib import OAuth1Session
import os
from datetime import datetime
from asyncio import sleep as s
# from webserver import keep_alive
import discord
from discord.ext import tasks, commands
from discord import Intents
from discord import app_commands
from discord import colour
from discord import Streaming
from discord.utils import get
import discord
from discord import app_commands, ui
import tweepy
from dotenv import load_dotenv
load_dotenv()

class aclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.synced = False

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

# Logs exception to .txt file.
def log_and_print_exception(e):
    logging_file = open("log.txt", "a")
    logging_file.write(f"{datetime.now()}\n{str(e)}\n\n")
    logging_file.close()
    print(f"Exception logged. Error:\n{e}")

# Gets a twitter account's latest tweet.
def checktwitter(twitter_name, self=None):
    id = (int(get_channel(1)))
    #channel = client.get_channel(id)
    user = twitclient.get_user(username=twitter_name) # Takes in plain text uername (id) and turns it into user information.
    tweets = twitclient.get_users_tweets(user.data.id, exclude='replies,retweets') # Takes the user information and turns it into a user id to be used for get_users_tweets. Then grabs the 10 latest tweets.
    #message = ""
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
        with open('streams.txt', 'r') as file:
            streams = (file.read())
            streamlist = streams.split(",")
            if f"\nhttps://twitch.tv/{twitch_name}" in message.content:
                file.close()
                return message
    else:
        return False

# Checks if a tweet has already been sent
async def has_tweet_already_sent(channel, tweet_id):
    async for message in channel.history(limit=200):
        with open('streams.txt', 'r') as file:
            streams = (file.read())
            streamlist = streams.split(",")
            if f'https://vxtwitter.com/twitter/statuses/{tweet_id}' in message.content:
                file.close()
                return message
    else:
        return False

# 0=botlog, 1=tweets, 2=streams, 3=modmail
def get_channel(id):
    file = open('channels.txt', "r")
    channels = file.read()
    channel_list = channels.split(",")
    try:
        requestname = client.get_channel(int(channel_list[id]))
        request = channel_list[id]
    # streamlist.remove(f'{twitch_name}')
    # newstreams = ",".join(streamlist)
    #print(f' the requested channel is {requestname}')
    except:
        print("Channel not listed listed in channel file!")
    file.close()
    return request

# Contains the live event loop.
@client.event
async def on_ready():
    await discord.Client.wait_until_ready(client)
    if not client.synced:
        await tree.sync(guild= discord.Object(id=980108559226380318))
        self.synced = True
    print(f"Bot has logged in.")
    # Defines a loop that will run every 10 seconds (checks for live users every 10 seconds).

    @tasks.loop(seconds=30)
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
                    # else:
                    #     print("Tweet has already been sent")
            if streams != "":
                # Gets the guild, 'twitch streams' channel, and streaming role.
                #guild = client.get_guild(980108559226380318)
                channel = client.get_channel(int(get_channel(2)))
                # role = get(guild.roles, id=980827359232004156)
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
                        #thumbnail_url_first_part = stream_data['data'][0]['thumbnail_url'].split('{')
                        #full_thumbnail_url = f"{thumbnail_url_first_part[0]}1920x1080.jpg"
                        # Checks to see if the live message has already been sent.
                        message = await has_notif_already_sent(channel, twitch_name)
                        if message is not False:
                            continue
                        await channel.send(
                            f":red_circle: **LIVE**"
                            #f"\n{user.mention} is now playing {stream_data['data'][0]['game_name']} on Twitch!"
                            f"\n@here Come watch!"
                            #f"\n{stream_data['data'][0]['title']}", file=discord.File(fp=buffer, filename="thumbnail.jpg"))
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
        
class AnnounceDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(AnnounceDropdown())

@tree.command(name="announce", description=f'Sends a message to the specified channel as the bot.', guild= GUILD_ID)
async def self(interaction: discord.Interaction, message: str):
    print(message)
    view= AnnounceDropdownView()
    with open('temp_announcement.txt', 'w') as file:
        file.writelines(message)
    file.close()
        
    #id = int(get_channel(4))
    #Announcement_Channel = client.get_channel(id)
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
    embed.add_field(name="hello", value="The bot will respond back with a simple 'Hello @you!'")
    embed.add_field(name="help", value="Sends this message!")
    embed.add_field(name="ping", value="Checks the latency of the bot. Responds with 'Pong! **ms'")
    #embed.add_field(name="", value="")

    embed.timestamp = datetime.now()
    await user.send(embed=embed)
    
    #await user.send('lol trolled\nhttps://tenor.com/view/rickroll-roll-rick-never-gonna-give-you-up-never-gonna-gif-22954713')

# Pong!
@tree.command(name="ping", description=f'Reports latency.', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong! {round(client.latency * 1000)}ms')

# Friendly bot :)
@tree.command(name="hello", description=f'Has the bot say Hi', guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    author = interaction.user
    await interaction.response.send_message(f'Hello {author.mention}!')

@client.event
async def on_member_join(member):
    #currentchannel = client.get_channel(980108559918456917)
    botlog = client.get_channel(int(get_channel(0)))
    #content = interaction.message
    guildname = client.fetch_guild.__name__
    #member = discord.member(member)
    await member.send(f'Welcome to {guildname} {member.mention}!')
    try:
        roles = [role for role in member.roles[1:]]
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"{member}",
            description=f"{member.mention}")
        embed.add_field(name="**ID**", value=f"{member.id}", inline=True)
        # embed.add_field(name="**•Status•**", value=str(member.status).replace("dnd", "Do Not Disturb"), inline=True)
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
        #embed.set_footer(text=f'ID: {member.id}  •  {datetime.strftime(fmt="%m, %d, %y", self=member)}')
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
        #embed.set_footer(text=f'ID: {member.id}  •  {datetime.strftime(fmt="%m, %d, %y", self=member)}')
        embed.timestamp = datetime.now()
        await botlog.send(embed=embed)
        # await botlog.send(f'{message.author.mention} has joined.')
    await client.wait_until_ready()

class TeamModal(ui.Modal, title='Team Information'):
    TeamName = discord.ui.TextInput(label='Team Name', required=True)
    Players = discord.ui.TextInput(label= "Player IDs", default= "Master Nox#6330, Master Nox#6330, Master Nox#6330", required=True)
    #Player1 = discord.ui.TextInput(label= "Player 1 ID", default= "Master Nox#6330", required=True)
    #Player2 = discord.ui.TextInput(label= "Player 2 ID", default= "BluBlazing#7777", required=True)
    #Player3 = discord.ui.TextInput(label= "Player 3 ID", default= "Planet#9951", required=True)
    Subs = discord.ui.TextInput(label= "Sub IDs", default= "BluBlazing#7777, BluBlazing#7777, BluBlazing#7777", required=True)
    #Subs = discord.ui.Select(options=[discord.SelectOption(label='Yes Subs'), discord.SelectOption(label='No Subs')])
    RankInfo = discord.ui.TextInput(label="Average Team Rank", default="0", required=True)

    with open(f'./{TeamName} Match Info.txt', 'w') as file:
        file.write(f'{TeamName}\n{Players}\n{Subs}\n{RankInfo}')
        file.close
    
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
        await interaction.response.send_message("Your information has been recorded and sent as follows.",embed=embed, ephemeral=True)

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
    #print(TeamName1)
    Team1Players = x.children[0].view.Players.value
    #print(Team1Players)
    Team1Subs = x.children[0].view.Subs.value
    #print(Team1Subs)
    Team1Rank = x.children[0].view.RankInfo.value
    #print(Team1Rank)
    #with open( )
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
    await user.send(embed=embed)
    
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