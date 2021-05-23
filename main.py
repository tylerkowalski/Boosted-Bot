import discord
from riotwatcher import LolWatcher
#imports the file with the API keys
import config

#creates an instance of the class "Client", which will act as the connection to discord
client = discord.Client()

@client.event
async def on_ready():
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")

#creates an instance of the class LolWatcher    
lol_watcher = LolWatcher(config.RIOT_API_KEY)
my_region = "na1"






# @client.event
# async def on_message(message):
    #does nothing if message is outputted by the bot
    # if message.author == client.user:
    #     return

    # if message.content.startswith("?boosted"):
    #     await message.channel.send("haha")

client.run(config.DISCORD_API_KEY)
