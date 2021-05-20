import discord

#imports the file with the token
import config

client = discord.Client()

@client.event
async def on_ready():
    print("BOOSTED BOT IS ONLINE".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("?boosted"):
        luka_counter = 0
        spencer_counter = 0
        await message.channel.send("haha")

client.run(config.TOKEN)
