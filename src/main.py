import discord
from discord.ext import commands, tasks
import requests
from discord.ext.commands import Bot
#imports the file with the API keys and other confidential information
import config

#returns the JSON file with the summonder id # 
def get_id(name):
    output = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + config.RIOT_API_KEY)
    return(output.json())

def get_ranked_data(ID):
    output = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + ID + "?api_key=" + config.RIOT_API_KEY)
    return(output.json())

help_command = commands.DefaultHelpCommand(no_category = "Commands")
#creates an instance of the class "Bot", which will act as the connection to discord, and sets the trigger to "?"
bot = Bot(command_prefix= "?", help_command = help_command)

#command to find current rank of given NA summoner
@bot.command(name = "rank", help = "find the current rank of an NA summoner")
async def ranked_stats(ctx, league_name):
    idJSON = get_id(league_name)
    ranked_dataJSON = get_ranked_data(idJSON["id"])

#finds the index of the dictionary in the JSON file containing stats on solo queue
    for k in range(len(ranked_dataJSON)):
        if str(ranked_dataJSON[k]["queueType"]) == "RANKED_SOLO_5x5":
            index = k

    tier = str(ranked_dataJSON[index]["tier"])
    division = str(ranked_dataJSON[index]["rank"])
    wins = str(ranked_dataJSON[index]["wins"])
    losses = str(ranked_dataJSON[index]["losses"])
    LP = str(ranked_dataJSON[index]["leaguePoints"])
    win_percentage = str(round((float(wins) / (float(wins) + float(losses))* 100), 2))

    await ctx.channel.send(league_name + " is " + tier + " " + division + " " + LP + "LP" + "\n" + wins + " wins and " + losses + " losses with a " + win_percentage + "% win percentage" + "\nsmells like BOOOOOOOOOOOOOOOOOSTED")

@tasks.loop(seconds = 3)
async def recent_game_checker():
    print("hello")




@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(name = "FINDING THE MOST BOOSTED SWINE", type = 5))
    
    #starts the game checking loop
    recent_game_checker.start()
    
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")

bot.run(config.DISCORD_API_KEY)
