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

#intializes these timestamps to be used by the below function
most_recent_timestamp_SPENCER = 0
most_recent_timestamp_LUKA = 0

#finds initial timestamps for Spencer and Luka's matchlists
def most_recent_timestamp_finder(most_recent_timestamp_SPENCER, most_recent_timestamp_LUKA):
    initial_JSON_SPENCER = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + config.SPENCER_ACCOUNT_ID + "?queue=420&season=13&api_key=" + config.RIOT_API_KEY)
    most_recent_timestamp_SPENCER = initial_JSON_SPENCER.json()["matches"][0]["timestamp"]
    initial_JSON_LUKA = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + config.LUKA_ACCOUNT_ID + "?queue=420&season=13&api_key=" + config.RIOT_API_KEY)
    most_recent_timestamp_LUKA = initial_JSON_LUKA.json()["matches"][0]["timestamp"]
    print(most_recent_timestamp_SPENCER)
    print(most_recent_timestamp_LUKA)


@tasks.loop(seconds = 4)
async def recent_game_checker(most_recent_timestamp_SPENCER, most_recent_timestamp_LUKA):
    print("checking...")
    boosted_bot_channel = bot.get_channel(config.BOOSTED_BOT_CHANNEL_ID)
    game_idJSON_SPENCER = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + config.SPENCER_ACCOUNT_ID + "?queue=420&season=13&beginTime=" + str(most_recent_timestamp_SPENCER) + "&api_key=" + config.RIOT_API_KEY)
    game_idJSON_LUKA = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + config.LUKA_ACCOUNT_ID + "?queue=420&season=13&beginTime=" + str(most_recent_timestamp_LUKA) + "&api_key=" + config.RIOT_API_KEY)
    
    if game_idJSON_SPENCER.json()["matches"][0]["timestamp"] != most_recent_timestamp_SPENCER:

        #sets a new most recent timestamp
        most_recent_timestamp_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["timestamp"] 

        # checks if there is a new game played, and if there is finds data regarding that match
        try:
            new_game_id_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["gameId"]
            new_game_champion_id_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["champion"]
            new_game_match_data_SPENCER = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + new_game_id_SPENCER + "?api_key=" + config.RIOT_API_KEY)
        
            #parses through stats of every summoner in the game to find Spencer
            for i in range(9):
                if new_game_match_data_SPENCER.json()["participants"][i]["championId"] == str(new_game_champion_id_SPENCER):
                    if new_game_match_data_SPENCER.json()["participants"][i]["win"] == True:
                        boosted_bot_channel.send("Spencer just won a game!")
                    else:
                        boosted_bot_channel.send("Spencer just lost another game!") 
                break

        except:
            pass

    if game_idJSON_LUKA.json()["matches"][0]["timestamp"] != most_recent_timestamp_LUKA:
        
        #sets a new most recent timestamp
        most_recent_timestamp_LUKA = game_idJSON_LUKA.json()["matches"][0]["timestamp"]

        # checks if there is a new game played, and if there is finds data regarding that match
        try:
            new_game_id_LUKA = game_idJSON_LUKA.json()["matches"][0]["gameId"]
            new_game_champion_id_LUKA = game_idJSON_LUKA.json()["matches"][0]["champion"]
            new_game_match_data_LUKA = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + str(new_game_id_LUKA) + "?api_key=" + config.RIOT_API_KEY)

            #parses through stats of every summoner in the game to find Luka
            for i in range(9):
                if new_game_match_data_LUKA.json["participants"][i]["championId"] == new_game_champion_id_LUKA:
                    if new_game_match_data_LUKA.json["participants"][i]["win"] == True:
                        boosted_bot_channel.send("Luka just won a game!")
                    else:
                        boosted_bot_channel.send("Luka just lost another game!") 
                break
            
        except:
            pass

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(name = "FINDING THE MOST BOOSTED SWINE", type = 5))
    
    #finds the most recent timestamps for Luka and Spencer
    most_recent_timestamp_finder(most_recent_timestamp_SPENCER, most_recent_timestamp_LUKA)

    #starts the game checking loop
    recent_game_checker.start(most_recent_timestamp_SPENCER, most_recent_timestamp_LUKA)
    
    #prints in terminal
    print("BOOSTED BOT IS ONLINE")


# boosted_bot_channel = bot.get_channel(config.BOOSTED_BOT_CHANNEL_ID)
# current_time = time.time() * 1000
# LUKA_JSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + config.LUKA_ACCOUNT_ID + "?queue=420&season=13" + "&api_key=" + config.RIOT_API_KEY)
# print(len(LUKA_JSON.json()["matches"]))
# # print(LUKA_JSON.json())
# # print(LUKA_JSON.json()["matches"][0]["gameId"])
# try:
#     new_game_id_LUKA = LUKA_JSON.json()["matches"][0]["gameId"]
#     new_game_champion_id_LUKA = LUKA_JSON.json()["matches"][0]["champion"]
#     new_game_match_data_LUKA = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + str(new_game_id_LUKA) + "?api_key=" + config.RIOT_API_KEY)

#     print("test0")
#     print(new_game_match_data_LUKA.json()["participants"][0]["championId"])
#     #parses through stats of every summoner in the game to find Luka
#     for i in range(9):
#         if new_game_match_data_LUKA.json()["participants"][i]["championId"] == new_game_champion_id_LUKA:
#             print("test1")
#             print(new_game_match_data_LUKA.json()["participants"][i]["stats"]["win"])
#             if new_game_match_data_LUKA.json()["participants"][i]["stats"]["win"] == False:
#                 print("test2")
#             else:
#                 print("test3")
#             print("hello??")
#             break
# except Exception as e:
#     print(e)

#starts the discord bot
bot.run(config.DISCORD_API_KEY)
