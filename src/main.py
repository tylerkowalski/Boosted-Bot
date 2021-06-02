import discord
from discord.ext import commands, tasks
import requests
from discord.ext.commands import Bot
#imports the file with the API keys and other confidential information
import config


#creates an instance of the class "Bot", which will act as the connection to discord, and sets the trigger to "?"
bot = Bot(command_prefix= "?", help_command = commands.DefaultHelpCommand(no_category = "Commands"))


#returns the JSON file with the summonder id # 
def get_id(name):
    output = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + config.RIOT_API_KEY)
    return(output.json())

def get_ranked_data(ID):
    output = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + ID + "?api_key=" + config.RIOT_API_KEY)
    return(output.json())

#finds initial timestamps for Spencer and Luka's matchlists
def most_recent_timestamp_finder(account_id):
    initial_JSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id + "?queue=420&season=13&api_key=" + config.RIOT_API_KEY)
    return initial_JSON.json()["matches"][0]["timestamp"]
   

#intializes these timestamps using most_recent_timestamp
most_recent_timestamp_SPENCER = most_recent_timestamp_finder(config.SPENCER_ACCOUNT_ID)
most_recent_timestamp_LUKA = most_recent_timestamp_finder(config.LUKA_ACCOUNT_ID)

@tasks.loop(seconds = 4)
async def recent_game_checker(boosted_bot_channel):
    # print("checking...")

    #makes it so that these global variables can be changed by the function
    global most_recent_timestamp_SPENCER
    global most_recent_timestamp_LUKA
    game_idJSON_SPENCER = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + config.SPENCER_ACCOUNT_ID + "?queue=420&season=13&beginTime=" + str(most_recent_timestamp_SPENCER) + "&api_key=" + config.RIOT_API_KEY)
    game_idJSON_LUKA = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + config.LUKA_ACCOUNT_ID + "?queue=420&season=13&beginTime=" + str(most_recent_timestamp_LUKA) + "&api_key=" + config.RIOT_API_KEY)
    print(game_idJSON_SPENCER.json())
    try:
        if game_idJSON_SPENCER.json()["matches"][0]["timestamp"] != most_recent_timestamp_SPENCER:
            print("test1")
            #sets a new most recent timestamp
            most_recent_timestamp_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["timestamp"]
            print("test2")
            new_game_id_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["gameId"]
            print("test3")
            new_game_champion_id_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["champion"]
            print("test4")
            new_game_match_dataJSON_SPENCER = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + str(new_game_id_SPENCER) + "?api_key=" + config.RIOT_API_KEY)
            print("test5")
            #parses through stats of every summoner in the game to find Spencer
            for i in range(9):
                print(new_game_match_dataJSON_SPENCER.json()["participants"][i]["championId"])
                print(new_game_champion_id_SPENCER)
                
                if new_game_match_dataJSON_SPENCER.json()["participants"][i]["championId"] == new_game_champion_id_SPENCER:
                    print("test6")
                    if new_game_match_dataJSON_SPENCER.json()["participants"][i]["stats"]["win"] == True:
                        await boosted_bot_channel.send("Spencer just won a game!")

                    else:
                        await boosted_bot_channel.send("Spencer just lost another game!") 
                    break

        if game_idJSON_LUKA.json()["matches"][0]["timestamp"] != most_recent_timestamp_LUKA:

            #sets a new most recent timestamp
            most_recent_timestamp_LUKA = game_idJSON_LUKA.json()["matches"][0]["timestamp"]

            new_game_id_LUKA = game_idJSON_LUKA.json()["matches"][0]["gameId"]
            new_game_champion_id_LUKA = game_idJSON_LUKA.json()["matches"][0]["champion"]
            new_game_match_dataJSON_LUKA = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + new_game_id_LUKA + "?api_key=" + config.RIOT_API_KEY)

            #parses through stats of every summoner in the game to find Luka
            for i in range(9):
                if new_game_match_dataJSON_LUKA.json()["participants"][i]["championId"] == new_game_champion_id_LUKA:
                    if new_game_match_dataJSON_LUKA.json()["participants"][i]["stats"]["win"] == True:
                        await boosted_bot_channel.send("Luka just won a game!")
                    else:
                        await boosted_bot_channel.send("Luka just lost another game!") 
                    break
    except Exception as e:
        print(e)

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



@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(name = "FINDING THE MOST BOOSTED SWINE", type = 5))
    
    #creates the output channel for the bot
    boosted_bot_channel = bot.get_channel(config.BOOSTED_BOT_CHANNEL_ID)

    #starts the game checking loop
    recent_game_checker.start(boosted_bot_channel)
    
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")

# TESTJSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/3929031449?api_key=" + config.RIOT_API_KEY)
# print(TESTJSON.json()["participants"][1]["championId"])

#starts the discord bot
bot.run(config.DISCORD_API_KEY)
