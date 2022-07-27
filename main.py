from __future__ import print_function
from cProfile import label
from email import message
from errno import EPERM
from gettext import find
import json
import string
from xml.etree.ElementTree import tostring
from pandas import describe_option
import requests
from lib2to3.pytree import convert
from msilib.schema import File, TextStyle
from socket import timeout
from tkinter import Button
import requests
from requests_oauthlib import OAuth1Session
import os
import re
from datetime import datetime, timedelta
from asyncio import sleep as s, wait
# from webserver import keep_alive
import discord
from discord.ext import tasks, commands, menus
import discord.ext
from discord import Intents, InteractionMessage, InteractionResponse, Message, Reaction
from discord import app_commands
from discord import colour
from discord import Streaming
from discord.utils import get
import discord
from discord import app_commands, ui
import tweepy
import http.client
from typing import Callable, List, Optional
import sys
from dotenv import load_dotenv
load_dotenv()

#sys.stdout = open('log.txt', 'w')

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

GUILD_ID = guild= discord.Object(id= 979262254958657576)

# Twitter auth
twitclient = tweepy.Client(bearer_token=os.getenv('twit_bearer_token'),
                       consumer_key=os.getenv('twit_consumer_key'),
                       consumer_secret=os.getenv('twit_consumer_secret'),
                       access_token=os.getenv('twit_access_token'),
                       access_token_secret=os.getenv('twit_access_token_secret'))
twitclient.wait_on_rate_limit=True

start_time = datetime.now()

ctx: commands.Context

@client.event
async def on_disconnect():
    uptimedelta = datetime.now() - start_time
    print('ShowtimeRL Bot disconnected at ' + datetime.ctime(datetime.now()) + '. ShowtimeRL Bot has been up for ' + str(timedelta(seconds=uptimedelta.seconds)))
    #sys.stdout.close()

@client.event
async def on_resumed():
    uptimedelta = datetime.now() - start_time
    print("ShowtimeRL Bot reconnected at  " + datetime.ctime(datetime.now()) + '. ShowtimeRL Bot has been up for ' + str(timedelta(seconds=uptimedelta.seconds)))
    #sys.stdout = open('log.txt', 'w')

@client.event
async def on_connect():
    print('ShowtimeRL Bot was connected starting at ' + datetime.ctime(datetime.now()))

def date_check(input):
    pattern = re.compile(r"20[0-9]{2}-(0[0-9]|1[0-2])-(0[0-9]|1[0-9]|2[0-9]|3[0-1])", re.IGNORECASE)
    return pattern.match(input)

def time_check(input):
    pattern = re.compile(r"([01]?[0-9]|2[0-3]):[0-5][0-9]", re.IGNORECASE)
    return pattern.match(input)

# Logs exception to .txt file.
def log_and_print_exception(e):
    # Could have the bot message me any errors is encounters.
    Nox = client.fetch_user(208383176781856768)
    Nox.send(f'Error occurred:\n{str(e)}')
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

def listToStringCommaSpace(s):
    str1 = ", "
    
    return (str1.join(s))

def listToStringComma(s):
    str1 = ","
    
    return (str1.join(s))

# Contains the live event loop.
@client.event
async def on_ready():
    await discord.Client.wait_until_ready(client)
    if not client.synced:
        await tree.sync(guild= GUILD_ID)
        self.synced = True
    print(f"Bot has logged in.")
    
    @tasks.loop(hours=24)
    async def todays_matchs():
        
        # Eventually place an if statement here that checks if its between certain hours.
                
        today = datetime.today().strftime("%Y-%m-%d")
        year, month, day = today.rsplit('-')
        
        year = int(year)
        month = int(month)
        day = int(day)
        
        if month == 1:
            monthname = 'January'
            monthlength = 31
        elif month == 2:
            monthname = 'February'
            if year == 2024:
                monthlength = 29
            monthlength = 28
        elif month == 3:
            monthname = 'March'
            monthlength = 31
        elif month == 4:
            monthname = 'April'
            monthlength = 0
        elif month == 5:
            monthname = 'May'
            monthlength = 31
        elif month == 6:
            monthname = 'June'
            monthlength = 30
        elif month == 7:
            monthname = 'July'
            monthlength = 31
        elif month == 8:
            monthname = 'August'
            monthlength = 31
        elif month == 9:
            monthname = 'September'
            monthlength = 30
        elif month == 10:
            monthname = 'October'
            monthlength = 31
        elif month == 11:
            monthname = 'November'
            monthlength = 0
        elif month == 12:
            monthname = 'December'
            monthlength = 31
            
        print(f'\nRemoving Matches prior to {monthname} {day} {year}.\nCurrent time is: {datetime.now()}\n')
        
        with open('Matches.txt', 'r') as file:
            data = file.readlines()
        file.close()
        
        tobedeleted = []
        upcomingmatches = []
        
        index = 0
        for line in data:
            if line.startswith('Date: '):
                date = line.replace('Date: ', '')
                MatchYear, MatchMonth, MatchDay = date.rsplit('-')
                
                MatchYear = int(MatchYear)
                MatchMonth = int(MatchMonth)
                MatchDay = int(MatchDay)
                
                remainingdays = day+7-monthlength
                if remainingdays > 0:
                                        
                    if MatchYear < year:
                        tobedeleted.append(index)
                    elif MatchYear == year and MatchMonth < month:
                        tobedeleted.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay < day:
                        tobedeleted.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day:
                        upcomingmatches.append(index)    
                    
                    index2 = 1
                    while remainingdays > 0:
                        newmonth = month+1
                                                  
                        if newmonth == 13:
                            newmonth = 1
                            year += 1
                        
                        if MatchYear == year and MatchMonth == newmonth and MatchDay == index2:
                            upcomingmatches.append(index)
                        index2 += 1
                        remainingdays -=1
                    
                
                if remainingdays <= 0:
                    if MatchYear < year:
                        tobedeleted.append(index)
                    elif MatchYear == year and MatchMonth < month:
                        tobedeleted.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay < day:
                        tobedeleted.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day+1:
                        upcomingmatches.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day+2:
                        upcomingmatches.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day+3:
                        upcomingmatches.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day+4:
                        upcomingmatches.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day+5:
                        upcomingmatches.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day+6:
                        upcomingmatches.append(index)
                    elif MatchYear == year and MatchMonth == month and MatchDay == day+7:
                        upcomingmatches.append(index)
                        
            index+=1

        for i in tobedeleted:
            data[i-1] = ''
            data[i] = ''
            data[i+1] = ''
            data[i+2] = ''
            data[i+3] = ''
        
        with open('Matches.txt', 'w') as file:
            file.writelines(data)
        file.close()
        
        
        matchname = []
        matchdate = []
        matchtime = []
        matchproducers = []
                
        for i in upcomingmatches:
            matchname.append(data[i-1])
            matchdate.append(str(data[i]).replace('Date: ', ''))
            matchtime.append(str(data[i+1]).replace('Time: ', ''))
            matchproducers.append(str(data[i+2]).replace('Producers: ', ''))
        
        if len(upcomingmatches) != 0:
            emb = discord.Embed(
                color= discord.colour.Color.random()
            )
            emb.add_field(name='| **Teams**', value=listToStringNewline(matchname), inline=True)
            emb.add_field(name='| **Date**', value=listToStringNewline(matchdate), inline=True)
            emb.add_field(name='| **Time**', value=listToStringNewline(matchtime), inline=True)
            
            channel = client.get_channel(int(get_channel(5)))
                        
            await channel.send('<@&986715160880242799>\nThe Matches for the next 7 days are: ', embed=emb)
            
            
            index4 = 0
            for i in upcomingmatches:
                
                team1, team2 = str(data[i-1]).split(' VS. ')
                with open('Teams.txt', 'r') as file:
                    data2 = file.readlines()
                file.close()
                
                index3 = 0
                for line in data2:
                    if line.startswith(f'Team Name: {team1}'):
                        team1Cap = str(data2[index3-2]).replace('Captain: ', '')
                        team1Players = str(data2[index3+1]).replace('Team Players: ', '')
                        team1Subs = str(data2[index3+2]).replace('Team Subs: ', '')
                        team1Rank = data2[index3+3].replace('Average Team Rank: ', '')
                    if line.startswith(f'Team Name: {team2}'):
                        team2Cap = data2[index3-2].replace('Captain: ', '')
                        team2Players = data2[index3+1].replace('Team Players: ', '')
                        team2Subs = data2[index3+2].replace('Team Subs: ', '')
                        team2Rank = data2[index3+3].replace('Average Team Rank: ', '')
                    index3 +=1
                
                MatchInfo = discord.Embed(
                    color = discord.colour.Color.random()
                )
                MatchInfo.add_field(name='**Team 1 Name**', value=team1, inline=True).add_field(name='**Team 2 Name**', value=team2, inline=True).add_field(name='\u200b', value='\u200b')
                MatchInfo.add_field(name='**Team 1 Captain**', value=team1Cap, inline=True).add_field(name='**Team 2 Captain**', value=team2Cap, inline=True).add_field(name='\u200b', value='\u200b')
                MatchInfo.add_field(name='**Team 1 Players**', value=team1Players, inline=True).add_field(name='**Team 2 Players**', value=team2Players, inline=True).add_field(name='\u200b', value='\u200b')
                MatchInfo.add_field(name='**Team 1 Subs**', value=team1Subs, inline=True).add_field(name='**Team 2 Subs**', value=team2Subs, inline=True).add_field(name='\u200b', value='\u200b')
                MatchInfo.add_field(name='**Team 1 Rank**', value=team1Rank, inline=True).add_field(name='**Team 2 Rank**', value=team2Rank, inline=True).add_field(name='\u200b', value='\u200b')
                MatchInfo.add_field(name='**Date**', value=matchdate[index4], inline=True).add_field(name='**Time**', value=matchtime[index4], inline=True).add_field(name='\u200b', value='\u200b')
                if matchproducers[index4] != '\n':
                    MatchInfo.add_field(name="Producers", value=matchproducers[index4], inline=False)
                else:
                    MatchInfo.add_field(name="Producers", value="None", inline=False)

                # Will need to attatch a view to the message for the producers to sign up for matches. 
                # Will also need to create another loop for reminders about said matches. Will likely require a file to track the producers OR have them added to Matches.txt
                
                view = ProducerSignupView(i)

                
                await channel.send('', embed=MatchInfo, view=view)
                index4 += 1


                
                
        else:
            channel = client.get_channel(int(get_channel(5)))
            await channel.send('<@&986715160880242799>\nNo Matches in the next 7 days.')
        
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
    todays_matchs.start()
    live_notifs_loop.start()

class ProducerSignupView(discord.ui.View):
    def __init__(self, matchindex):
        self.matchindex = matchindex
        super().__init__(timeout=86400)
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Sign Up', style=discord.ButtonStyle.green, custom_id='STRL:ProdYes')
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        with open('Matches.txt', 'r') as file:
            data = file.readlines()
        file.close()
        
        if data[self.matchindex+2].find(str(interaction.user)) == -1:
        
            data[self.matchindex+2] = str(data[self.matchindex+2]).rstrip() +str(f' {interaction.user}\n')
            
            with open('Matches.txt', 'w') as file:
                file.writelines(data)
            file.close()
                    
            team1, team2 = str(data[self.matchindex-1]).split(' VS. ')
            with open('Teams.txt', 'r') as file:
                data2 = file.readlines()
            file.close()
            
            index3 = 0
            for line in data2:
                if line.startswith(f'Team Name: {team1}'):
                    team1Cap = str(data2[index3-2]).replace('Captain: ', '')
                    team1Players = str(data2[index3+1]).replace('Team Players: ', '')
                    team1Subs = str(data2[index3+2]).replace('Team Subs: ', '')
                    team1Rank = data2[index3+3].replace('Average Team Rank: ', '')
                if line.startswith(f'Team Name: {team2}'):
                    team2Cap = data2[index3-2].replace('Captain: ', '')
                    team2Players = data2[index3+1].replace('Team Players: ', '')
                    team2Subs = data2[index3+2].replace('Team Subs: ', '')
                    team2Rank = data2[index3+3].replace('Average Team Rank: ', '')
                index3 +=1
            
            MatchInfo = discord.Embed(
                color = discord.colour.Color.random()
            )
            MatchInfo.add_field(name='**Team 1 Name**', value=team1, inline=True).add_field(name='**Team 2 Name**', value=team2, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Captain**', value=team1Cap, inline=True).add_field(name='**Team 2 Captain**', value=team2Cap, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Players**', value=team1Players, inline=True).add_field(name='**Team 2 Players**', value=team2Players, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Subs**', value=team1Subs, inline=True).add_field(name='**Team 2 Subs**', value=team2Subs, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Rank**', value=team1Rank, inline=True).add_field(name='**Team 2 Rank**', value=team2Rank, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Date**', value=data[self.matchindex].replace('Date: ', ''), inline=True).add_field(name='**Time**', value=data[self.matchindex+1].replace('Time: ', ''), inline=True).add_field(name='\u200b', value='\u200b')
            if data[self.matchindex+2].replace('Producers: ', '') != '\n':
                MatchInfo.add_field(name="Producers", value=data[self.matchindex+2], inline=False)
            else:
                MatchInfo.add_field(name="Producers", value="None", inline=False)

            await interaction.response.edit_message(content='', embed=MatchInfo)
            
            await interaction.followup.send(f"{interaction.user.mention} you've signed up for the match.", ephemeral=True)
            
        else:
            await interaction.response.send_message(f'{interaction.user.mention} you are already signed up for this match.', ephemeral=True)
            
        self.value = "✔️"
        #self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red, custom_id='STRL:ProdNo')
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        
        with open('Matches.txt', 'r') as file:
            data = file.readlines()
        file.close()
        
        if data[self.matchindex+2].find(str(interaction.user)) != -1:
            data[self.matchindex+2]= data[self.matchindex+2].replace(f' {str(interaction.user)}', ' ')
            
            with open('Matches.txt', 'w') as file:
                file.writelines(data)
            file.close()
            
            team1, team2 = str(data[self.matchindex-1]).split(' VS. ')
            with open('Teams.txt', 'r') as file:
                data2 = file.readlines()
            file.close()
            
            index3 = 0
            for line in data2:
                if line.startswith(f'Team Name: {team1}'):
                    team1Cap = str(data2[index3-2]).replace('Captain: ', '')
                    team1Players = str(data2[index3+1]).replace('Team Players: ', '')
                    team1Subs = str(data2[index3+2]).replace('Team Subs: ', '')
                    team1Rank = data2[index3+3].replace('Average Team Rank: ', '')
                if line.startswith(f'Team Name: {team2}'):
                    team2Cap = data2[index3-2].replace('Captain: ', '')
                    team2Players = data2[index3+1].replace('Team Players: ', '')
                    team2Subs = data2[index3+2].replace('Team Subs: ', '')
                    team2Rank = data2[index3+3].replace('Average Team Rank: ', '')
                index3 +=1
            
            
            MatchInfo = discord.Embed(
                color = discord.colour.Color.random()
            )
            MatchInfo.add_field(name='**Team 1 Name**', value=team1, inline=True).add_field(name='**Team 2 Name**', value=team2, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Captain**', value=team1Cap, inline=True).add_field(name='**Team 2 Captain**', value=team2Cap, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Players**', value=team1Players, inline=True).add_field(name='**Team 2 Players**', value=team2Players, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Subs**', value=team1Subs, inline=True).add_field(name='**Team 2 Subs**', value=team2Subs, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Team 1 Rank**', value=team1Rank, inline=True).add_field(name='**Team 2 Rank**', value=team2Rank, inline=True).add_field(name='\u200b', value='\u200b')
            MatchInfo.add_field(name='**Date**', value=data[self.matchindex].replace('Date: ', ''), inline=True).add_field(name='**Time**', value=data[self.matchindex+1].replace('Time: ', ''), inline=True).add_field(name='\u200b', value='\u200b')
            if data[self.matchindex+2].replace('Producers: ', '') != '\n':
                MatchInfo.add_field(name="Producers", value=data[self.matchindex+2], inline=False)
            else:
                MatchInfo.add_field(name="Producers", value="None", inline=False)

            
            await interaction.response.edit_message(content='', embed=MatchInfo)
            
            await interaction.followup.send(f"{interaction.user.mention} you've quit the match.", ephemeral=True)
        else:
            await interaction.response.send_message(f'{interaction.user.mention} you are not signed up for this match.', ephemeral=True)
        
        self.value = "❌"
        #self.stop()
        
    async def on_timeout(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.value = "Timeout"
        self.stop()
    

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
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"Command List")
        embed.add_field(name="General Commands", value='**hello** - The bot will respond back with a simple "Hello @you!"\n**help** - Sends this message.\n**ping** - Checks the latency of the bot. Responds with "Pong! **ms"', inline=False)
        embed.add_field(name="Showmatch Commands", value="**create/edit/delete_team** - These three commands are used to manage your team within the Showmatch system.\n**match_request** - This commands lets you set up a match against another team within the Showmatch system.\n**cancel_match** - This command lets you cancel a match that you have already created.", inline=False)
        embed.add_field(name='Information Commands', value="**team/match_info** - These commands allows you to look up a corresponding match or team and see their corresponding information.\n**list_teams/matches** - These commands let you see all teams and matches currently listed within the showmatch system.", inline=False)
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
        
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
@app_commands.describe(twitter_name='Name of the twitter you want to add to the system.')
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
@app_commands.describe(twitter_name='Name of the twitter you want to remove from the system.')
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
         await interaction.response.send_message(f'The currently tracked twitters include: {tweeters}')
         file.close()

# This command lets you add a streamer to the notification list.
@tree.command(name="stream_add", description=f'Adds a Twitch to the live notifs.', guild= GUILD_ID)
@app_commands.describe(twitch_name='Name of the streamer you want to add to the system.')
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
@app_commands.describe(twitch_name='Name of the streamer you want to remove from the system.')
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
async def change_channel(self, chosen_channel, chosen_function):

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
    elif chosen_function == "Producer Channel":
        chosen_function = 5
        
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
    def __init__(self, function):
        self.function = function
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_name_list.append(channel.name)
                    text_channel_id_list.append(channel.id)
        
        if len(text_channel_name_list) > 11:
            text_channel_name_list[11] = "[Next Page]"
            del text_channel_name_list[12:]
            
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
        if self.values[0] != '[Next Page]':
            id = text_channel_id_list[text_channel_name_list.index(self.values[0])]
            await change_channel(self, id, self.function)
            await interaction.response.send_message(f"You chose <#{id}>\nThe Bot is now updated.", ephemeral=True)
            
            botid = int(get_channel(0))
            botchannel = client.get_channel(botid)
            
            await botchannel.send(f"{interaction.user.mention} changed the {self.function} to <#{id}>")
        else:
            view = ChannelDropDownExtendedView(PageNumber=2, function=self.function)
            await interaction.response.edit_message(content=f"You chose the **{self.function}** function.\nNow choose which channel you'd like to attach it to.", view=view)

class ChannelDropdownExtended(discord.ui.Select):
    def __init__(self, PageNumber, function):
        self.PageNumber = PageNumber
        self.function = function
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_name_list.append(channel.name)
                    text_channel_id_list.append(channel.id)
                    
        
        Listings = 10*self.PageNumber
        try:
            text_channel_name_list[Listings+1] = "[Next Page]"
            del text_channel_name_list[Listings+2:]
            del text_channel_name_list[0:Listings-9]
        except:
            end = len(text_channel_name_list)
            del text_channel_name_list[0:end-10]
        
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
        if self.values[0] != '[Next Page]':
            id = text_channel_id_list[text_channel_name_list.index(self.values[0])]
            await change_channel(self, id)
            await interaction.response.send_message(f"You chose <#{id}>\nThe Bot is now updated.", ephemeral=True)
            
            botid = int(get_channel(0))
            botchannel = client.get_channel(botid)
            
            
            await botchannel.send(f"{interaction.user.mention} changed the {self.function} to <#{id}>")
        else:
            view = ChannelDropDownExtendedView(self.PageNumber+1, function= self.function)
            await interaction.response.edit_message(content = f"You chose the **{self.function}** function.\nNow choose which channel you'd like to attach it to.", view=view)

# Used in /setchannel, has the info for the function select dropdown.
class FunctionDropdown(discord.ui.Select):
    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Bot Log', emoji='⬛'),
            discord.SelectOption(label='Tweet Channel', emoji='🟦'),
            discord.SelectOption(label='Stream Channel', emoji='🟪'),
            discord.SelectOption(label='Mod Mail', emoji='🟥'),
            discord.SelectOption(label="Announcement Channel", emoji='⬜'),
            discord.SelectOption(label="Producer Channel", emoji='🟧')
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
        view = ChannelDropdownView(function = self.values[0])
        
        await interaction.response.send_message(f"You chose the **{self.values[0]}** function.\nNow choose which channel you'd like to attach it to.", view=view, ephemeral=True)

# Creates the view for the Function Dropdown.
class FunctionDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FunctionDropdown())

# Creates the view for the Channel Dropdown.
class ChannelDropdownView(discord.ui.View):
    def __init__(self, function):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(ChannelDropdown(function= function))

class ChannelDropDownExtendedView(discord.ui.View):
    def __init__(self, PageNumber, function):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(ChannelDropdownExtended(PageNumber, function))

# Replaces the old set commands and combines them into 1 elegant solution.
@tree.command(name="setchannel", description="Lets you set various channels.", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    view = FunctionDropdownView()
    await interaction.response.send_message('Choose a function to change.', view=view, ephemeral=True)

# Lists channels the bot is outputting too.
@tree.command(name="mod_channel_list", description=f"Display all bot configured channels", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f"The current channels are:\nBot Log: <#{int(get_channel(0))}>\nTweet Channel: <#{int(get_channel(1))}>\nStream Channel: <#{int(get_channel(2))}>\nMod-Mail Channel: <#{int(get_channel(3))}>\nAnnouncement Channel: <#{int(get_channel(4))}>")

# Used in /announce, contains the dropdown to select the proper channel.
class AnnounceDropdown(discord.ui.Select):
    def __init__(self, message):
        self.message = message
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_name_list.append(channel.name)
                    text_channel_id_list.append(channel.id)
                    
        if len(text_channel_name_list) > 10:
            text_channel_name_list[11] = "[Next Page]"
            del text_channel_name_list[12:]
                    
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
        
        if self.values[0] != '[Next Page]':
            id = text_channel_id_list[text_channel_name_list.index(self.values[0])]
            Announcement_Channel = client.get_channel(id)
            BotLog = client.get_channel(int(get_channel(0)))
            
            await interaction.response.send_message("Your message has been sent!", ephemeral=True)
            await BotLog.send(f'{interaction.user.mention} sent the message "{self.message}" using the bot in <#{id}>')
            await Announcement_Channel.send(f"{self.message}")
        else:
            view = AnnounceDropdownExtendedView(PageNumber=2, message=self.message)
            await interaction.response.edit_message(content = f"What channel would you like to send a message to?", view=view)
            
          
class AnnounceDropdownExtended(discord.ui.Select):
    def __init__(self, PageNumber, message):
        self.PageNumber = PageNumber
        self.message = message
        text_channel_name_list = []
        text_channel_id_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel.type) == 'text':
                    text_channel_name_list.append(channel.name)
                    text_channel_id_list.append(channel.id)
                    
        
        Listings = 10*self.PageNumber
        try:
            text_channel_name_list[Listings+1] = "[Next Page]"
            del text_channel_name_list[Listings+2:]
            del text_channel_name_list[0:Listings-9]
        except:
            end = len(text_channel_name_list)
            del text_channel_name_list[0:end-10]
                
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
        if self.values[0] != '[Next Page]':
            id = text_channel_id_list[text_channel_name_list.index(self.values[0])]
            Announcement_Channel = client.get_channel(id)
            BotLog = client.get_channel(int(get_channel(0)))
            
            await interaction.response.send_message("Your message has been sent!", ephemeral=True)
            await BotLog.send(f'{interaction.user.mention} sent the message "{self.message}" using the bot in <#{id}>')
            await Announcement_Channel.send(f"{self.message}")
        else:
            view = AnnounceDropdownExtendedView(self.PageNumber+1, message = self.message)
            await interaction.response.edit_message(content = f"What channel would you like to send a message to?", view=view)
        
# Creates the view for the Announce Dropdown.
class AnnounceDropdownView(discord.ui.View):
    def __init__(self, message):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(AnnounceDropdown(message))
        
class AnnounceDropdownExtendedView(discord.ui.View):
    def __init__(self, PageNumber, message):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(AnnounceDropdownExtended(PageNumber, message))

# Lets the user say things through the bot in a specified channel.
@tree.command(name="say", description=f'Sends a message to the specified channel as the bot.', guild= GUILD_ID)
@app_commands.describe(message='The message you want the bot to send.')
async def self(interaction: discord.Interaction, message: str):
    view= AnnounceDropdownView(message)
        
    await interaction.response.send_message("What channel would you like to send a message to?", view=view, ephemeral=True)
    
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
    embed.add_field(name="General Commands", value='**hello** - The bot will respond back with a simple "Hello @you!"\n**help** - Sends this message.\n**ping** - Checks the latency of the bot. Responds with "Pong! **ms"', inline=False)
    embed.add_field(name="Showmatch Commands", value="**create/edit/delete_team** - These three commands are used to manage your team within the Showmatch system.\n**match_request** - This commands lets you set up a match against another team within the Showmatch system.\n**cancel_match** - This command lets you cancel a match that you have already created.", inline=False)
    embed.add_field(name='Information Commands', value="**team/match_info** - These commands allows you to look up a corresponding match or team and see their corresponding information.\n**list_teams/matches** - These commands let you see all teams and matches currently listed within the showmatch system.", inline=False)
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
        
        await interaction.response.send_message("Your information has been recorded and sent as follows.",embed=embed, ephemeral=True)

class ConfirmDeny(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=10800)
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
        
    async def on_timeout(self, interaction: discord.Interaction):
        await interaction.response.send_message("This request has timed out.")
        self.value = "Timeout"
        self.stop()

class ConfirmDenyDeletion(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=10800)
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

    async def on_timeout(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.value = "Timeout"
        self.stop()

# Modal to gather team information.
class TeamModal2(ui.Modal, title='Team Information'):
    TeamName = discord.ui.TextInput(label='Team Name', required=True)
    Players = discord.ui.TextInput(label= "Player IDs", default= "Master Nox#6330, Master Nox#6330, Master Nox#6330", required=True)
    Subs = discord.ui.TextInput(label= "Sub IDs", default= "BluBlazing#7777, BluBlazing#7777, BluBlazing#7777", required=True)
    RankInfo = discord.ui.TextInput(label="Average Team Rank", default="0", required=True)
    
    async def on_submit(self, interaction):
        
        await interaction.response.send_message("Please enter your team information.", ephemeral=True)

# Modal class to edit already existing team info.
class TeamInfoEdit(ui.Modal, title='Edit Team Information'):
    TeamName = discord.ui.TextInput(label='Team Name', required=True)
    Players = discord.ui.TextInput(label= "Player IDs", default= "Master Nox#6330, Master Nox#6330, Master Nox#6330", required=True)
    Subs = discord.ui.TextInput(label= "Sub IDs", default= "BluBlazing#7777, BluBlazing#7777, BluBlazing#7777", required=True)
    RankInfo = discord.ui.TextInput(label="Average Team Rank", default="0", required=True)
        
    async def on_submit(self, interaction):
        await interaction.response.defer()

# Attatchement Class.
class TeamEditView(discord.ui.View):
    def __init__(self, author, Teams):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(TeamEditView2(author, Teams))

# Dropdown view for teams that the author is the Captain of.
class TeamEditView2(discord.ui.Select):
    def __init__(self, author, Teams: list):
        self.author = author
        self.Teams = Teams
        options = [
            discord.SelectOption(label=key)
            for key in Teams
        ]
        super().__init__(placeholder='Choose a team..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
                
        x = TeamInfoEdit()
        await interaction.response.send_modal(x)
        await TeamInfoEdit.wait(x)
        
        with open('Teams.txt', 'r') as file:
            data = file.readlines()
        file.close()
        
        writtenin = str(x.children[0].view.TeamName)
        chosen = self.Teams[self.Teams.index(self.values[0])]
        
        flag = False
        for line in data:
            if line.startswith(f'Team Name: {x.children[0].view.TeamName}'):
                if writtenin != chosen:
                    flag = True
                elif writtenin == chosen:
                    flag = False
                    
        if flag == False:
                
            index = -2
            with open('Teams.txt', 'r') as file:
                for line in file:
                    index +=1
                    if line == f'Team Name: {self.values[0]}\n':
                        break
            file.close()
            
            data[index] = f'Captain: {self.author}\n'
            data[index] = f'Captain ID: {self.author.id}\n'
            data[index+1] = f'Team Name: {x.children[0].view.TeamName}\n'
            data[index+2] = f'Team Players: {x.children[0].view.Players}\n'
            data[index+3] = f'Team Subs: {x.children[0].view.Subs}\n'
            data[index+4] = f'Average Team Rank: {x.children[0].view.RankInfo}\n'
            
            with open(f'Teams.txt', 'w') as file:
                file.writelines(data)
            file.close()
            
            await interaction.followup.send(f"Team **{x.children[0].view.TeamName}** has been updated.", ephemeral=True)
            
        elif flag == True:
            await interaction.followup.send(f'A team by the name of **{x.children[0].view.TeamName}**, already exists. Please choose a different name.', ephemeral=True)
        
# Attatchement Class.
class MatchView(discord.ui.View):
    def __init__(self, author, enemy_captain, Teams: list, date, time):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(MatchView2(author, enemy_captain, Teams, date, time))

# Dropdown view for teams that the author is the Captain of.
class MatchView2(discord.ui.Select): 
    def __init__(self, author, enemy_captain, Teams: list, date, time):
        self.author = author
        self.enemy_captain = enemy_captain
        self.date = date
        self.time = time
        
        index = 0
        for Team in Teams:
            Teams[index] = Team.rstrip('\n')
            index +=1
                        
        options = [
            discord.SelectOption(label=key)
            for key in Teams
        ]
        super().__init__(placeholder='Choose a team..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        
        self.author_teams = self.values[0]
        
        
        # author = self.author
        enemycaptain = self.enemy_captain.id
        
        Teams = []
        flag2 = 0

        with open('Teams.txt', 'r') as file:
            for line in file:
                if line.startswith("Captain ID: "):
                    if f"{enemycaptain}" in line:
                        flag2 = 1
                    else:
                        flag2 = 0
                if flag2 == 1:
                    TeamName = str(file.readline())
                    TeamName = TeamName.replace("Team Name: ", "")
                    TeamName = TeamName.rstrip("\n")
                    Teams.append(TeamName)
                    flag2 = 0
        file.close()
        
        view = OpponentMatchView(self.author, self.author_teams, Teams, self.date, self.time)
        
        await interaction.response.send_message(f"Choose which team you want to play against.", view= view, ephemeral=True)

class OpponentMatchView(discord.ui.View):
    def __init__(self, author, author_teams, enemy_teams, date, time):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(OpponentMatchView2(author, author_teams, enemy_teams, date, time))

class OpponentMatchView2(discord.ui.Select):
    def __init__(self, author, author_teams, enemy_teams, date, time):
        self.author = author
        self.author_teams = author_teams
        self.date = date
        self.time = time
        
        
        options = [
            discord.SelectOption(label=key)
            for key in enemy_teams
        ]
        super().__init__(placeholder='Choose a team..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        
        index = 0
        
        author = self.author
        authorid = int(author.id)
        
        with open('Teams.txt', 'r') as file:
            data = file.readlines()
        file.close()
        
        TeamtoSend = self.author_teams
        
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
        embed.add_field(name="**Proposed Date**", value=f"{self.date}", inline=True)
        embed.add_field(name="**Proposed Time**", value=f"{self.time}", inline=True)
        embed.add_field(name="**Team Name**", value=f"{TeamName}", inline=False)
        embed.add_field(name=f"**Players**", value=f"{TeamPlayers}", inline=True)
        embed.add_field(name=f"**Subs**", value=f"{TeamSubs}", inline=True)
        embed.add_field(name="**Average Rank**", value=f"{TeamRank}", inline=False)
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(f"Your match request has been sent to the captain of **{self.values[0]}**.", ephemeral=True)
        
        view = ConfirmDeny()
        await Captain.send(embed=embed, view=view)
        await ConfirmDeny.wait(view)
        
        if view.children[0].view.confirm.view.value == "✔️":
            await Author.send(f"Your opponent {Captain} has accepted the match!")
            
            TeamName = TeamName.replace('\n', '')
            
            Title = TeamName + " VS. " + str(self.values[0])
            
            with open(f'./Matches.txt', 'a') as file:
                file.writelines(f'{TeamName} VS. {str(self.values[0])}\nDate: {self.date}\nTime: {self.time}\nProducers: \n\n')
            file.close()
            
            
            
            payload = { 'Title': Title,
            'Date': self.date,
            'Time': self.time}
            session = requests.Session()
            session.post('https://eor82olfyhrllj.m.pipedream.net',data=payload)
        
        elif view.children[0].view.deny.view.value == "❌":
            await Author.send(f"Your opponent {Captain} has denied the match!")
            
        else:
            await Author.send(f"Your opponent {Captain} did not respond to the request.")
                
class DeleteTeamView(discord.ui.View):
    def __init__(self, TeamCaptain, Teams):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(DeleteTeamView2(TeamCaptain, Teams))

# Dropdown view for teams that the author is the Captain of.
class DeleteTeamView2(discord.ui.Select):
    def __init__(self, TeamCaptain, Teams):
        self.TeamCaptain = TeamCaptain

        options = [
            discord.SelectOption(label=key)
            for key in Teams
        ]
        super().__init__(placeholder='Choose a team to delete..', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
    
        view = ConfirmDenyDeletion()
        await interaction.response.send_message(f"Please confirm in DM's.", ephemeral=True)
        await self.TeamCaptain.send(f'Are you certain you want to delete team **{self.values[0]}**?', view=view)
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
            
            if data[index-2] == f'Captain ID: {self.TeamCaptain.id}\n' and flag == 1:
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
                await self.TeamCaptain.send(f"Team **{self.values[0]}** has been deleted.")
            else:
                await self.TeamCaptain.send('Something went wrong. Contact Master Nox#6330 if the problem persists.')
        else:
            await self.TeamCaptain.send(f"Deletion cancelled.")
        
@tree.command(name="match_request", description="Sets up a match within the showmatch system. Date Format: YYYY-MM-DD. Time Format: HH:MM CST.", guild= GUILD_ID)
@app_commands.describe(enemy_captain = "@ of the enemy team's captain.", date = "YYYY-MM-DD", time = "HH:MM in CST." )
async def self(interaction: discord.Interaction, enemy_captain: discord.user.User, date: str, time: str):
    author = interaction.user
    EndEarly = False
    if date_check(date) == None:
        await interaction.response.send_message('Your date was entered incorrectly. Please use the format YYYY-MM-DD.', ephemeral=True)
        print(f'{author} entered the date incorrectly when using /match_request.')
        EndEarly = True
        if time_check(time) == None:
            await interaction.followup.send('Your time was entered incorrectly. Please use the format HH:MM.', ephemeral=True)
            print(f'{author} entered the time incorrectly when using /match_request.')
    
    if time_check(time) == None and EndEarly == False:
        await interaction.response.send_message('Your time was entered incorrectly. Please use the format HH:MM.', ephemeral=True)
        print(f'{author} entered the time incorrectly when using /match_request.')
        EndEarly = True
        
    if EndEarly != True:
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
                    Teams.append(TeamName)
                    flag2 = 0
        file.close()
        
        view = MatchView(author, enemy_captain, Teams, date, time)
        
        if flag == 0:
            await interaction.response.send_message("You are not listed as a captain for any of the teams in our database.", ephemeral=True)
        elif flag == 1:
            await interaction.response.send_message("Please select your team.", view = view, ephemeral=True)
     
     
class MultiMatchSelectView(discord.ui.View):
    def __init__(self, Matches, data, author, EnemyCap, Options):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(MultiMatchSelectView2(Matches, data, author, EnemyCap, Options))
     
class MultiMatchSelectView2(discord.ui.Select):
    def __init__(self, Matches, data, author, EnemyCap, Options):
        self.data = data
        self.author = author
        self.EnemyCap = EnemyCap
        self.Matches = Matches
        options = [
            discord.SelectOption(label=key)
            for key in Options
        ]
        super().__init__(placeholder='Choose a match.', min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        view = ConfirmDenyDeletion()
        await interaction.response.send_message('Match found, are you sure you want to cancel this match?', ephemeral=True, view = view)
        await ConfirmDenyDeletion.wait(view)
        
        if view.children[0].view.confirm.view.value == "✔️":
            await interaction.followup.send("Confirmed. Removing match and notifying opposing team.", ephemeral=True)
            
            await self.EnemyCap.send(f'{self.author} has cancelled the match **{self.values[0]}**.')
            self.data[self.Matches[0]] = ''
            self.data[self.Matches[0]+1] = ''
            self.data[self.Matches[0]+2] = ''
            self.data[self.Matches[0]+3] = ''
            
            with open('Matches.txt', 'w') as file:
                file.writelines(self.data)
            file.close()
        else:
            await interaction.followup.send('Denied, the match has not been modified.', ephemeral=True)
        
@tree.command(name='cancel_match', guild=GUILD_ID, description="Cancel a match.")
@app_commands.describe(match_name = 'Name of the match you wish to cancel. "Team 1 VS. Team 2"')
async def self(interaction: discord.Interaction, match_name: str):
    author = interaction.user
    
    match_name = match_name.rstrip()
    
    with open('Matches.txt', 'r') as file:
        data = file.readlines()
    file.close()
    
    MatchExists = False
    MatchingMatches = []
    
    index = 0
    for line in data:
        if line.startswith(f'{match_name}'):
            MatchExists = True
            MatchingMatches.append(index)
        index += 1
    
    
    team1, team2 = match_name.split(' VS. ')
        
    with open('Teams.txt', 'r') as file:
        data2 = file.readlines()
    file.close()
    
    index2 = 0
    for line in data2:
        if line.startswith(f'Team Name: {team1}'):
            team1cap = data2[index2-2].replace('Captain: ', '')
            team1cap = team1cap.rstrip()
        if line.startswith(f'Team Name: {team2}'):
            team2cap = data2[index2-2].replace('Captain: ', '')
            team2cap = team2cap.rstrip()
        index2 += 1
    
    
    TheyAreInMatch = False
    if team1cap == str(author):
        TheyAreInMatch = True
        EnemyCap = interaction.guild.get_member_named(team2cap)
    if team2cap == str(author):
        TheyAreInMatch = True
        EnemyCap = interaction.guild.get_member_named(team1cap)  
    
    if MatchExists == False:
        await interaction.response.send_message('No match found under that name, please ensure you type the match name correctly.', ephemeral=True)
    elif MatchExists == True and len(MatchingMatches) > 1:
        if TheyAreInMatch == True:
            # Needs a select view.
            Options = []
            OptionsIndex = 1
            for i in MatchingMatches:
                Name = data[i].rstrip()
                Date = data[i+1].rstrip()
                Time = data[i+2].rstrip()
                Options.append(f'{OptionsIndex}: {Name} {Date} {Time}')
                OptionsIndex += 1
            
            view = MultiMatchSelectView(MatchingMatches, data, author, EnemyCap, Options)
            await interaction.response.send_message('Multiple matches found under that name, please choose one.', ephemeral=True, view = view)
            
        else:
            await interaction.response.send_message('You are not listed as the captain for either team in this match.', ephemeral=True)
        
    elif MatchExists == True and len(MatchingMatches) == 1:
        if TheyAreInMatch == True:
            view = ConfirmDenyDeletion()
            await interaction.response.send_message('Match found, are you sure you want to cancel this match?', ephemeral=True, view = view)
            await ConfirmDenyDeletion.wait(view)
            
            if view.children[0].view.confirm.view.value == "✔️":
                await interaction.followup.send("Confirmed. Removing match and notifying opposing team.", ephemeral=True)
                
                await EnemyCap.send(f'{author} has cancelled the match **{match_name}**.')
                data[MatchingMatches[0]] = ''
                data[MatchingMatches[0]+1] = ''
                data[MatchingMatches[0]+2] = ''
                data[MatchingMatches[0]+3] = ''
                data[MatchingMatches[0]+4] = ''
                
                with open('Matches.txt', 'w') as file:
                    file.writelines(data)
                file.close()
                
            else:
                await interaction.followup.send('Denied, the match has not been modified.', ephemeral=True)  
        else:
            await interaction.response.send_message('You are not listed as the captain for either team in this match.', ephemeral=True)
            
        
@tree.command(name="edit_team", guild= GUILD_ID, description="Lets you edit one of your team's information.")
async def self(interaction:discord.Interaction):
    author = interaction.user
    authorid = author.id
    
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
    if flag == 0:
        await interaction.response.send_message("You are not listed as a captain for any of the teams in our database.", ephemeral=True)
    elif flag == 1:
        view = TeamEditView(author=author, Teams=Teams)
        await interaction.response.send_message("Please select the team you'd lke to edit.", view = view, ephemeral=True)
          
@tree.command(name="create_team", guild= GUILD_ID, description="Opens a form and saves that newly created team to the database.")
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
    flag = []
    flag2 = []
    flag3 = False
    
    with open('Teams.txt', 'r') as file:
        data = file.readlines()
    file.close()
    
    for line in data:
        if line.startswith(f'Captain: {TeamCaptain}'):
            flag.append(index)
        if line.startswith(f'Team Name: {TeamName}'):
            flag2.append(index)
        index += 1
    
    for i in flag:
        for j in flag2:
            if i+2 == j:
                flag3 = True
    
    if flag3 == True:
        await interaction.followup.send(f"You are already listed as the Captain for **{TeamName}** in our database, consider /edit_team instead.", ephemeral=True)
    elif len(flag2) > 0 and flag3 != True:
        await interaction.followup.send(f'A team by the name of **{TeamName}**, already exists within our database, please choose a different name.', ephemeral=True)
    else:
        with open('Teams.txt', 'a') as file:
            file.writelines(f"Captain: {TeamCaptain}\nCaptain ID: {CaptainID}\nTeam Name: {TeamName}\nTeam Players: {TeamPlayers}\nTeam Subs: {TeamSubs}\nAverage Team Rank: {TeamRank}\n\n")
        file.close()
        await interaction.followup.send(f"Info for **{TeamName}** has been recorded.", ephemeral=True)
    
@tree.command(name='delete_team', guild= GUILD_ID, description="Used to delete a team that you own.")
async def self(interaction: discord.Interaction):
    TeamCaptain = interaction.user
    CaptainID = TeamCaptain.id
    
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
    
    view = DeleteTeamView(TeamCaptain, Teams)
    
    if flag == 0:
        await interaction.response.send_message("You are not listed as a captain for any of the teams in our database.", ephemeral=True)
    elif flag == 1:
        await interaction.response.send_message("Please select the team you wish to delete.", view = view, ephemeral=True)
    
# Page buttons are broken. They work but give a response failed error. Look into Fixing
class Paginator(discord.ui.View):
    r"""A dynamic paginator that uses a callback to generate embeds.
    This should be passed in as a regular view to methods like
    :meth:`discord.abc.Messageable.send`.
    Parameters
    -----------
    callback: Callable[[:class:`int`], List[:class:`discord.Embed`]]
        The callback that takes in a page number and returns a list of
        :class:`discord.Embed`\s.
    pages: :class:`int`
        The page count, i.e. the last page the callback can generate.
    Attributes
    -----------
    page: :class:`int`
        The current page on the paginator.
    """

    def __init__(self,
                 callback: Callable[[int], List[discord.Embed]],
                 pages: int,
                 interaction: discord.Interaction,
                 **kwargs):
        super().__init__(**kwargs)
        self.pages = pages
        self.callback = callback
        self.page = 1
        self.interaction = interaction
        self._update_buttons()

    def _update_buttons(self):
        self.prev_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.pages

    def get_page(self, page: int) -> List[discord.Embed]:
        """Returns a page generated by the callback. Technically
        an alias for `Paginator.callback()`.
        Useful for getting an embed before deploying a View.
        """

        return self.callback(page)

    @discord.ui.button(label="previous")
    async def prev_button(self, _, interaction: discord.Interaction):
        self.page = max(self.page - 1, 1)
        self._update_buttons()
        embs = self.callback(self.page)
        await self.interaction.edit_original_message(embeds=embs, view=self)
        await interaction.response.defer()

    @discord.ui.button(label="next")
    async def next_button(self, _, interaction: discord.Interaction):
        self.page = min(self.page + 1, self.pages)
        self._update_buttons()
        embs = self.callback(self.page)
        await self.interaction.edit_original_message(embeds=embs, view=self)
        
class StaticPaginator(Paginator):
    """A simple paginator that takes in lines instead of a callback.
    A line limit and base embed may be passed in for customization.
    
    Parameters
    -----------
    lines: List[:class:`str`]
        The list of strings to iterate through in the paginator,
        joined in the output embed's description with newlines.
    line_limit: Optional[:class:`int`]
        The amount of lines to display per page. Defaults to 15.
    base_embed: Optional[:class:`discord.Embed`]
        The template for the resulting embed. Only the description will
        be replaced.
    """

    def __init__(self,
                 lines: List[str],
                 *,
                 line_limit: Optional[int] = 15,
                 base_embed: Optional[discord.Embed] = None,
                 **kwargs):
        self.lines = lines
        self.line_limit = line_limit
        self.base_embed = base_embed or discord.Embed()

        import math
        pages: int = math.ceil(len(lines) / self.line_limit)  # type: ignore

        def callback(page: int) -> List[discord.Embed]:
            m = (page-1) * self.line_limit  # type: ignore
            n = page * self.line_limit  # type: ignore

            emb = self.base_embed.copy()
            emb.description = "\n".join(self.lines[m:n])
            return [emb]

        super().__init__(callback, pages, **kwargs)
            
@tree.command(name='list_teams', guild= GUILD_ID, description="Lists all teams within the database.")
async def self(interaction: discord.Interaction):
    TeamNames = []
    Captains = []
    Ranks = []
    with open('Teams.txt', 'r') as file:
        for line in file:
            if line.startswith('Team Name: '):
                name = line.replace('Team Name: ', '')
                name = '| '+name
                name = name.rstrip()
                TeamNames.append(name)
            if line.startswith('Captain: '):
                Captain = line.replace('Captain: ', '')
                Captain = '| '+Captain
                Captain = Captain.rstrip()
                Captains.append(Captain)
            if line.startswith('Average Team Rank: '):
                Rank = line.replace('Average Team Rank: ', '')
                Rank = '| '+Rank
                Rank = Rank.rstrip()
                Ranks.append(Rank)
    file.close()
        
    Teams = len(TeamNames)
    TotalPages = 0
    while Teams >= 0:
        try:
            Teams -=10
            TotalPages +=1
        except:
            pass

    def embed_cat_page(page: int) -> List[discord.Embed]:
        display = page*10
        display2 = display-10
        embs = []
        emb = discord.Embed(
            color= discord.colour.Color.random()
        )
        emb.add_field(name='| **Team Name**', value=listToStringNewline(TeamNames[display2:display]), inline=True)
        emb.add_field(name='| **Captain**', value=listToStringNewline(Captains[display2:display]), inline=True)
        emb.add_field(name='| **Rank**', value=listToStringNewline(Ranks[display2:display]), inline=True)
        embs.append(emb)
        return embs

    view = Paginator(embed_cat_page, TotalPages, interaction)
    embs = view.get_page(1)
    
    await interaction.response.send_message(embeds=embs, view=view)
    # The next page button doesn't work because its interaction links to nothing. I tried moving the edit message down here but failed. I have yet to find a way to move the interaction up to the paginator.
    
@tree.command(name="role_test", guild= GUILD_ID)
async def self(interaction: discord.Interaction):
    view = Role_Buttons()
    await interaction.response.send_message("Test Role Message!", view=view)

@tree.command(name='list_matches', guild=GUILD_ID, description="Lists all upcoming matches and their times.")
async def self(interaction: discord.Interaction):
    today = datetime.today().strftime('%Y-%m-%d')
    
    with open('Matches.txt', 'r') as file:
        data = file.readlines()
    file.close()
    
    Matches = []
    Dates = []
    Times = []
    
    
    index = 0
    for line in data:

        if line.startswith('Date: '):
            Matches.append(data[index-1].replace('\n', ''))
            data[index] = data[index].replace('Date: ', '')
            Dates.append(data[index].replace('\n', ''))
            data[index+1] = data[index+1].replace('Time: ', '')
            Times.append(data[index+1].replace('\n', ''))
        index +=1

    NumofMatches = len(Matches)
    TotalPages = 0
    while NumofMatches >= 0:
        try:
            NumofMatches -=10
            TotalPages +=1
        except:
            pass

    def embed_match_page(page: int) -> List[discord.Embed]:
        display = page*10
        display2 = display-10
        embs = []
        emb = discord.Embed(
            color= discord.colour.Color.random()
        )
        emb.add_field(name='| **Teams**', value=listToStringNewline(Matches[display2:display]), inline=True)
        emb.add_field(name='| **Date**', value=listToStringNewline(Dates[display2:display]), inline=True)
        emb.add_field(name='| **Time**', value=listToStringNewline(Times[display2:display]), inline=True)
        embs.append(emb)
        return embs

    view = Paginator(embed_match_page, TotalPages, interaction)
    embs = view.get_page(1)
    
    await interaction.response.send_message(embeds=embs, view=view)
    
@tree.command(name='team_info', guild=GUILD_ID, description='Returns information on the requested team.')
@app_commands.describe(team_name='Name of the team you wish to get info for.')
async def self(interaction: discord.Interaction, team_name: str):
    with open('Teams.txt', 'r') as file:
        data = file.readlines()
    file.close()
    
    
    flag = False
    index = 0
    for line in data:
        if line.startswith(f'Team Name: {team_name}'):
            flag = True
            break
        index += 1
        
    if flag == True:
        teamCap = str(data[index-2]).replace('Captain: ', '')
        teamPlayers = str(data[index+1]).replace('Team Players: ', '')
        teamSubs = str(data[index+2]).replace('Team Subs: ', '')
        teamRank = data[index+3].replace('Average Team Rank: ', '')

                    
        TeamInfo = discord.Embed(
            color = discord.colour.Color.random()
        )
        TeamInfo.add_field(name='**Team Name**', value=team_name, inline=True)
        TeamInfo.add_field(name='**Team Captain**', value=teamCap, inline=True).add_field(name='\u200b', value='\u200b')
        TeamInfo.add_field(name='**Team Players**', value=teamPlayers, inline=True)
        TeamInfo.add_field(name='**Team Subs**', value=teamSubs, inline=True).add_field(name='\u200b', value='\u200b')
        TeamInfo.add_field(name='**Team Rank**', value=teamRank, inline=True)

        await interaction.response.send_message(embed=TeamInfo)
    else:
        await interaction.response.send_message('No team found by that name. Please ensure you typed it correctly.', ephemeral=True)

@tree.command(name='match_info', guild=GUILD_ID, description='Returns information about the requested match.')
@app_commands.describe(match_name='Name of the match you wish to get info for. "Team 1 VS. Team 2"')
async def self(interaction: discord.Interaction, match_name: str):
    with open('Matches.txt', 'r') as file:
        data = file.readlines()
    file.close()
    
    flag = False
    index = 0
    for line in data:
        if line.startswith(f'{match_name}'):
            flag = True
            break
        index += 1
    if flag == True:
        team1, team2 = str(data[index]).split(' VS. ')
        with open('Teams.txt', 'r') as file:
            data2 = file.readlines()
        file.close()
        
        index3 = 0
        for line in data2:
            if line.startswith(f'Team Name: {team1}'):
                team1Cap = str(data2[index3-2]).replace('Captain: ', '')
                team1Players = str(data2[index3+1]).replace('Team Players: ', '')
                team1Subs = str(data2[index3+2]).replace('Team Subs: ', '')
                team1Rank = data2[index3+3].replace('Average Team Rank: ', '')
            if line.startswith(f'Team Name: {team2}'):
                team2Cap = data2[index3-2].replace('Captain: ', '')
                team2Players = data2[index3+1].replace('Team Players: ', '')
                team2Subs = data2[index3+2].replace('Team Subs: ', '')
                team2Rank = data2[index3+3].replace('Average Team Rank: ', '')
            index3 +=1
        
        MatchInfo = discord.Embed(
            color = discord.colour.Color.random()
        )
        MatchInfo.add_field(name='**Team 1 Name**', value=team1, inline=True).add_field(name='**Team 2 Name**', value=team2, inline=True).add_field(name='\u200b', value='\u200b')
        MatchInfo.add_field(name='**Team 1 Captain**', value=team1Cap, inline=True).add_field(name='**Team 2 Captain**', value=team2Cap, inline=True).add_field(name='\u200b', value='\u200b')
        MatchInfo.add_field(name='**Team 1 Players**', value=team1Players, inline=True).add_field(name='**Team 2 Players**', value=team2Players, inline=True).add_field(name='\u200b', value='\u200b')
        MatchInfo.add_field(name='**Team 1 Subs**', value=team1Subs, inline=True).add_field(name='**Team 2 Subs**', value=team2Subs, inline=True).add_field(name='\u200b', value='\u200b')
        MatchInfo.add_field(name='**Team 1 Rank**', value=team1Rank, inline=True).add_field(name='**Team 2 Rank**', value=team2Rank, inline=True).add_field(name='\u200b', value='\u200b')
        MatchInfo.add_field(name='**Date**', value=data[index+1], inline=True).add_field(name='**Time**', value=data[index+2], inline=True).add_field(name='\u200b', value='\u200b')

        await interaction.response.send_message(embed=MatchInfo)
    
    if flag == False:
        await interaction.response.send_message('No match found by that name. Please ensure you typed it correctly.', ephemeral=True)
    
    
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