import requests
import tweepy
from requests_oauthlib import OAuth1Session
import json
# response = requests.get("http://api.open-notify.org/iss-now.json")
# json_response = response.json()
# dictionary = json.dumps(response.json(), sort_keys = True, indent = 4)
# print(dictionary)
#
#
# response = requests.get("http://api.open-notify.org/iss-now.json")
# longitude = json_response['iss_position']['longitude']
# latitude = json_response['iss_position']['latitude']
# print('Longitude: ', longitude)
# print('Latitude: ', latitude)

# response = requests.get('https://public-api.tracker.gg/v2/apex/standard/profile/psn/Daltoosh')
# TRNApiKey = '8f8782a3-53e3-4174-bdf6-9d4329ce0f72'
# dictionary = json.dumps(response.json(), sort_keys = True, indent = 4)
# print(dictionary)

twitclient = tweepy.Client(bearer_token='AAAAAAAAAAAAAAAAAAAAAI2sdAEAAAAACRZqQ5U8FtHWFRneAO9RpsLXYKw%3D1c2fy9NxTjHSJBKlMPu0y2jML0pPaN8RK1RLmGWgDoOQacB5bc',
                       consumer_key='mJ13DPNtROr9Smsxxh66tNvUU',
                       consumer_secret='e4h19jl8UKKwxC5bw5aDoDfma0ZW5aywGqWyEKn4P9xwspvFC4',
                       access_token='926253732-NKaTznqPfL8TEzSx3XSmeSwKt0JCD7MRqKpBvgiZ',
                       access_token_secret='2nzQUzX5J1Y23PSRpjwSvVzxgcqhXOZWAXo6QJ1Uw7vvY')

def apitest():

    url = "https://public-api.tracker.gg/v2/apex/standard/profile/psn/Daltoosh"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "TRN-Api-Key": "8f8782a3-53e3-4174-bdf6-9d4329ce0f72"
    }

    data = requests.get(url, headers=headers).json()
    print(json.dumps(data, indent=4))

def Showmatch(): # Remember that the bot needs a way to quit the process at any time. Also it should time out after 60 seconds.
    Team1 = str(input("Please enter the name of team 1"))
    while Team1 == "":
        Team1 = str(input("Please enter the name of team 1"))
    print(f'Log Output: Team 1 name:{Team1}')
    Team1Players = str(input("Please enter the players of team 1 separated by commas.")).split(",", 3)
    Team1Players = [x.strip(' ') for x in Team1Players]
    print(f'Log Output: Team 1 players:{Team1Players}')
    if str(input("Does Team 1 have any subs?")) == "Yes":
        Team1Subs = str(input("Please enter the subs for team 1 separated by commas.")).split(",")
        print(f'Log Output: Team 1 subs:{Team1Subs}')

def getTweet(client, id):
    user = twitclient.get_user(username=id) # Takes in plain text uername (id) and turns it into user information.
    tweets = twitclient.get_users_tweets(user.data.id) # Takes the user information and turns it into a user id to be used for get_users_tweets. Then grabs the 10 latest tweets.
    for tweet in tweets.data: # Cycles through all 10 tweets
        print('https://twitter.com/twitter/statuses/'+str(tweet.id)) # Prints URL to the tweet
        print(f'{tweet.text}\n') # Prints the text from that tweet

#class Showmatch2:


# class Square:
#    def __init__(self, length, width):
#        self.length = length
#        self.width = width
#    def area(self):
#        return self.width * self.length
# r = Square(20, 2000)
# print("Rectangle Area: %d" % (r.area()))

#Showmatch()
# apitest()
#print(getTweet(twitclient, "Master__Nox"))

