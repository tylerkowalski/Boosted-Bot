import discord
import requests
from discord.ext import commands
#imports the file with the API keys
import config

#returns the JSON file with the summonder id # 
def requestSummonerid(name):
    return requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + config.RIOT_API_KEY)











#creates an instance of the class "Client", which will act as the connection to discord
client = commands.Bot(command_prefix= "?")

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Activity(name = "FINDING THE BOOSTED SWINE", type = 5))
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")



client.run(config.DISCORD_API_KEY)
