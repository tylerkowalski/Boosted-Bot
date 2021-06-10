import asyncio
import discord
from discord.ext import commands
import requests
from discord.ext.commands import Bot
#imports the file with the API keys and other confidential information
import resources.config


#creates an instance of the class "Bot", which will act as the connection to discord and sets the trigger to "?"
bot = Bot(command_prefix= "?", help_command = commands.DefaultHelpCommand(no_category = "Commands"))
#finds initial timestamps for Spencer and Luka's matchlists
def most_recent_timestamp_finder(account_id):
    initial_JSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id + "?queue=420&season=13&api_key=" + resources.config.RIOT_API_KEY)
    return initial_JSON.json()["matches"][0]["timestamp"]

#called in recent_game_loop if a new ranked game has been detected
async def recent_game_checker(game_idJSON, name, boosted_bot_channel):
    new_game_id = game_idJSON.json()["matches"][0]["gameId"]
    new_game_champion_id = game_idJSON.json()["matches"][0]["champion"]
    new_game_match_dataJSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + str(new_game_id) + "?api_key=" + resources.config.RIOT_API_KEY)
    #parses through stats of every summoner in the game to find the desired summoner
    for i in range(10):
        if new_game_match_dataJSON.json()["participants"][i]["championId"] == new_game_champion_id:
            if new_game_match_dataJSON.json()["participants"][i]["stats"]["win"] == True:
                await boosted_bot_channel.send(name + " just won a game!")
            else:
                await boosted_bot_channel.send(name + " just lost another game!")
            break

#intializes these timestamps 
most_recent_timestamp_SPENCER = most_recent_timestamp_finder(resources.config.SPENCER_ACCOUNT_ID)
most_recent_timestamp_LUKA = most_recent_timestamp_finder(resources.config.LUKA_ACCOUNT_ID)

#checks if there was a new game played every 5 seconds
async def recent_game_loop(boosted_bot_channel):
    while True:     
        print("checking...")
        
        #makes it so that these global variables can be changed by the function
        global most_recent_timestamp_SPENCER
        global most_recent_timestamp_LUKA
        game_idJSON_SPENCER = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + resources.config.SPENCER_ACCOUNT_ID + "?queue=420&season=13&beginTime=" + str(most_recent_timestamp_SPENCER) + "&api_key=" + resources.config.RIOT_API_KEY)
        game_idJSON_LUKA = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + resources.config.LUKA_ACCOUNT_ID + "?queue=420&season=13&beginTime=" + str(most_recent_timestamp_LUKA) + "&api_key=" + resources.config.RIOT_API_KEY)
        try:
            if game_idJSON_SPENCER.json()["matches"][0]["timestamp"] != most_recent_timestamp_SPENCER:
                #sets a new most recent timestamp
                most_recent_timestamp_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["timestamp"]
                await recent_game_checker(game_idJSON_SPENCER, "Spencer", boosted_bot_channel)

            if game_idJSON_LUKA.json()["matches"][0]["timestamp"] != most_recent_timestamp_LUKA:
                #sets a new most recent timestamp
                most_recent_timestamp_LUKA = game_idJSON_LUKA.json()["matches"][0]["timestamp"]
                await recent_game_checker(game_idJSON_LUKA, "Luka", boosted_bot_channel)

        except Exception as e:
            print(e)
        await asyncio.sleep(5)

#command to find current rank of given NA summoner
@bot.command(name = "rank", help = "find the current rank of an NA summoner")
async def ranked_stats(ctx, league_name):
    try:

        idJSON = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + league_name + "?api_key=" + resources.config.RIOT_API_KEY)
        summoner_id = idJSON.json()["id"]
        ranked_dataJSON = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summoner_id + "?api_key=" + resources.config.RIOT_API_KEY)
        ranked_dataJSON = ranked_dataJSON.json()

        #finds the index of the dictionary in the JSON file containing stats on solo queue
        for k in range(len(ranked_dataJSON)):
            if str(ranked_dataJSON[k]["queueType"]) == "RANKED_SOLO_5x5":
                index = k
                break

        tier = str(ranked_dataJSON[index]["tier"])
        division = str(ranked_dataJSON[index]["rank"])
        wins = str(ranked_dataJSON[index]["wins"])
        losses = str(ranked_dataJSON[index]["losses"])
        LP = str(ranked_dataJSON[index]["leaguePoints"])
        win_percentage = str(round((float(wins) / (float(wins) + float(losses))* 100), 2))

        await ctx.channel.send(league_name + " is " + tier + " " + division + " " + LP + "LP" + "\n" + wins + " wins and " + losses + " losses with a " + win_percentage + "% win percentage" + "\nsmells like BOOOOOOOOOOOOOOOOOSTED")

    except Exception as e:
        print(e)
        await ctx.channel.send("GIVE ME A REAL NA SUMMONER! BRAIN GAP LOLOLOLLOL")


@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(name = "FINDING THE MOST BOOSTED SWINE", type = 5))

    #creates the output channel for the bot
    boosted_bot_channel = bot.get_channel(resources.config.BOOSTED_BOT_CHANNEL_ID)

    #adds the game checking loop into the event loop
    bot.loop.create_task(recent_game_loop(boosted_bot_channel))
    
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")

#connects the bot to discord and creates the event loop (bot)
bot.run(resources.config.DISCORD_API_KEY)
