import discord
import requests
from discord.ext.commands import Bot
#imports the file with the API keys
import config

#returns the JSON file with the summonder id # 
def request_id(name):
    return requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + config.RIOT_API_KEY)












#creates an instance of the class "Bot", which will act as the connection to discord
bot = Bot(command_prefix= "?")

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(name = "FINDING THE BOOSTED SWINE", type = 5))
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")

#there exists an issue with taking in the username, need to debug
@bot.command(name = "rank",)
async def rank(ctx, *league_name):
    idJSON = request_id(league_name)
    ID = idJSON[league_name]["id"]
    print(ID)

bot.run(config.DISCORD_API_KEY)
