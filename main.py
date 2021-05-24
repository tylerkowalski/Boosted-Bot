import discord
from discord.ext import commands
import requests
from discord.ext.commands import Bot
#imports the file with the API keys
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

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(name = "FINDING THE MOST BOOSTED SWINE", type = 5))
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")


@bot.command(name = "rank", help = "find the current rank of an NA summoner")
async def ranked_stats(ctx, league_name):
    idJSON = get_id(league_name)
    ranked_dataJSON = get_ranked_data(idJSON["id"])
    tier = str(ranked_dataJSON[0]["tier"])
    division = str(ranked_dataJSON[0]["rank"])
    wins = str(ranked_dataJSON[0]["wins"])
    losses = str(ranked_dataJSON[0]["losses"])
    LP = str(ranked_dataJSON[0]["leaguePoints"])
    win_percentage = str(round((float(wins) / (float(wins) + float(losses))* 100), 2))
    await ctx.channel.send(league_name + " is " + tier + " " + division + " " + LP + "LP" + "\n" + wins + " wins and " + losses + " losses with a " + win_percentage + "% win percentage" + "\nsmells like BOOOOOOOOOOOOOOOOOSTED")

bot.run(config.DISCORD_API_KEY)
