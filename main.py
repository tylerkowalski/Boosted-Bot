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
                team_ID = new_game_match_dataJSON.json()["participants"][i]["teamId"]
                boosted_score = await boosted_score_calculator(new_game_match_dataJSON, i, team_ID)
                await boosted_bot_channel.send(name + " just won a game, with a boosted score of " + str(boosted_score) + "!")
            else:
                await boosted_bot_channel.send(name + " just lost another game! LOLOLOLOLOLOL")
            break

#is only called when a game is won, shows the respective summoner's impact in that win
#the higher the boosted the score, the more boosted you are (postive is boosted, negative is not boosted)
async def boosted_score_calculator(game_match_data_JSON, participants_index, team_ID):
    kda_sum = 0
    boosted_score_kda_component = 0

    #takes the sum of your team's kdas, except the kda of the summoner in question
    for k in range(10):
        if k == participants_index or game_match_data_JSON.json()["participants"][k]["teamId"] != team_ID:
            pass
        else:
            kills = game_match_data_JSON.json()["participants"][k]["stats"]["kills"]
            assists = game_match_data_JSON.json()["participants"][k]["stats"]["assists"]
            deaths = game_match_data_JSON.json()["participants"][k]["stats"]["deaths"]
            kda = (kills + assists) / deaths
            kda_sum += kda

    kda_avg = kda_sum / 4
    
    player_kills = game_match_data_JSON.json()["participants"][participants_index]["stats"]["kills"]
    player_deaths = game_match_data_JSON.json()["participants"][participants_index]["stats"]["deaths"]
    player_assists = game_match_data_JSON.json()["participants"][participants_index]["stats"]["assists"]

    player_kda = (player_kills + player_assists) / player_deaths

    #finds how the summoner's kda compares to average on team, gives +/- score dependent on worse/better kda
    boosted_score_kda_component = round(0.5 * ((kda_avg / player_kda) - 1), 2)

    #finding average of gold/min deltas for summoner
    summoner_gold_per_min_sum = 0
    summoner_opponent_gold_per_min_sum = 0
    boosted_score_gold_diff_component = 0
    length_gold_per_min_deltas = len(game_match_data_JSON.json()["participants"][participants_index]["timeline"]["goldPerMinDeltas"])

    #the following keys that refer to specfic time deltas for gold diff in RIOT API (needed because some games don't have certain gold deltas as games could be shorter or longer)
    gold_diff_list = ["0-10", "10-20", "20-30", "30-end"]

    for k in range(length_gold_per_min_deltas):
        summoner_gold_per_min_sum += game_match_data_JSON.json()["participants"][participants_index]["timeline"]["goldPerMinDeltas"][gold_diff_list[k]]

    summoner_gold_per_min_avg = summoner_gold_per_min_sum / length_gold_per_min_deltas

    #finding the average of  gold/min deltas for summoner's lane opponent 
    summonner_role = game_match_data_JSON.json()["participants"][participants_index]["timeline"]["role"]
    summoner_lane = game_match_data_JSON.json()["participants"][participants_index]["timeline"]["lane"]
    
    for k in range(10):
        if game_match_data_JSON.json()["participants"][k]["timeline"]["role"] == summonner_role:
            if game_match_data_JSON.json()["participants"][k]["timeline"]["lane"] == summoner_lane:
                if k != participants_index:
                    for i in range(length_gold_per_min_deltas):
                        summoner_opponent_gold_per_min_sum += game_match_data_JSON.json()["participants"][k]["timeline"]["goldPerMinDeltas"][gold_diff_list[i]]
                    break
    
    summoner_opponent_gold_per_min_avg = summoner_opponent_gold_per_min_sum / length_gold_per_min_deltas

    #finds how the summoner's gold compares to lane opponent, gives +/- score dependent on less/more gold
    boosted_score_gold_diff_component = round(0.5 * ((summoner_opponent_gold_per_min_avg / summoner_gold_per_min_avg) - 1), 2)

    #returns boosted score
    return boosted_score_kda_component + boosted_score_gold_diff_component



#intializes these timestamps 
most_recent_timestamp_SPENCER = most_recent_timestamp_finder(resources.config.SPENCER_ACCOUNT_ID)

#checks if there was a new game played every 5 seconds
async def recent_game_loop(boosted_bot_channel):
    while True:     
        
        #makes it so that these global variables can be changed by the function
        global most_recent_timestamp_SPENCER
        game_idJSON_SPENCER = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + resources.config.SPENCER_ACCOUNT_ID + "?queue=420&season=13&beginTime=" + str(most_recent_timestamp_SPENCER) + "&api_key=" + resources.config.RIOT_API_KEY)
        try:
            if game_idJSON_SPENCER.json()["matches"][0]["timestamp"] != most_recent_timestamp_SPENCER:
                #sets a new most recent timestamp
                most_recent_timestamp_SPENCER = game_idJSON_SPENCER.json()["matches"][0]["timestamp"]
                await recent_game_checker(game_idJSON_SPENCER, "Spencer", boosted_bot_channel)

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
