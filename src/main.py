import asyncio
import discord
from discord.ext import commands
import requests
from discord.ext.commands import Bot
import sqlite3
import os
#imports the file with the API keys and other confidential information
import config


#creates paths necessary to access the boost_checker database in src
CURRENT_DIR = os.path.dirname(__file__)
BOOST_CHECKER_DIR_PATH = os.path.join(CURRENT_DIR, "boost_checker.db")



#creates an instance of the class "Bot", which will act as the connection to discord and sets the trigger to "?"
bot = Bot(command_prefix= "?", help_command = commands.DefaultHelpCommand(no_category = "Commands"))



#finds initial timestamps for summoners in the boost_check database
def most_recent_timestamp_finder(account_id):
    initial_JSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id + "?queue=420&season=13&api_key=" + config.RIOT_API_KEY)
    return initial_JSON.json()["matches"][0]["timestamp"]



#is only called when a game is won, shows the respective summoner's impact in that win
#the higher the boosted the score, the more boosted you are (postive is boosted, negative is not boosted)
def boosted_score_calculator(game_match_data_JSON, participants_index, team_ID):
    team_total_kills = 0
    team_kp_sum = 0

    #takes the sum of your team's kdas, except the kda of the summoner in question
    for k in range(10):
        if game_match_data_JSON.json()["participants"][k]["teamId"] != team_ID:
            pass
        else:
            team_total_kills += game_match_data_JSON.json()["participants"][k]["stats"]["kills"]
    
    #to ensure no division by zero
    if team_total_kills == 0:
        team_total_kills = 1
    else:
        pass

    for i in range(10):
        #doesn't include respective summoner's kp in sum to be more accurate in boosted score
        if game_match_data_JSON.json()["participants"][k]["teamId"] != team_ID or i == participants_index:
            pass
        else:
            team_kp_sum += 100 * ((game_match_data_JSON.json()["participants"][k]["stats"]["kills"] + game_match_data_JSON.json()["participants"][k]["stats"]["assists"])/team_total_kills)

    #calculates average kp of the summoner's teammates, excluding the summoner in question
    team_kp_avg = team_kp_sum / 4

    player_kp = 100 * ((game_match_data_JSON.json()["participants"][participants_index]["stats"]["kills"] + game_match_data_JSON.json()["participants"][participants_index]["stats"]["assists"])/team_total_kills)
    
    #to ensure no division by zero
    if player_kp == 0:
        player_kp = 1
    else:
        pass

    #finds how the summoner's kp compares to average on team (exclusive), gives +/- score dependent on worse/better kp
    boosted_score_kp_component = ((team_kp_avg / player_kp) - 1) * 50


    #finding summoner's gold
    summoner_gold = game_match_data_JSON.json()["participants"][participants_index]["stats"]["goldEarned"]
    
    #finding the total gold of the summoner's lane opponent
    summonner_role = game_match_data_JSON.json()["participants"][participants_index]["timeline"]["role"]
    summoner_lane = game_match_data_JSON.json()["participants"][participants_index]["timeline"]["lane"]
    
    
    #finds the index k in "participants" that corresponds to the summoner's lane opponent 
    for k in range(10):
        if game_match_data_JSON.json()["participants"][k]["timeline"]["role"] == summonner_role:
            if game_match_data_JSON.json()["participants"][k]["timeline"]["lane"] == summoner_lane:
                if k != participants_index:
                    #finds index which corresponds to summoner's opponent
                    opponent_index = k
                    break
    
    #finds summoner's opponent's  gold
    summoner_opponent_gold = game_match_data_JSON.json()["participants"][opponent_index]["stats"]["goldEarned"]
    #finds how the summoner's gold compares to lane opponent, gives +/- score dependent on less/more gold
    boosted_score_gold_diff_component = ((summoner_opponent_gold/ summoner_gold) - 1) * 50

    #returns boosted score
    return round(boosted_score_kp_component + boosted_score_gold_diff_component, 2)



#checks if there was a new game played 
async def recent_game_loop(boosted_bot_channel):
    while True:     
        
        #connects to the database
        db = sqlite3.connect(BOOST_CHECKER_DIR_PATH)
        cursor = db.cursor()

        #makes a list of summoners currently in database that need to be checked for boosted-ness
        cursor.execute("SELECT * FROM boost_check")
        database_list = cursor.fetchall()
        database_list_length = len(database_list)

        for k in range(database_list_length):
        
            #could query with the beginTime = timestamp_in_database, but I find that with this extra query, RIOT takes longer to update the timestamps, for whatever reason. As a result, this is a better method
            game_idJSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + str(database_list[k][1]) + "?queue=420&season=13&api_key=" + config.RIOT_API_KEY)
            try:
                #finds if a new game has been played based on timestamps
                if game_idJSON.json()["matches"][0]["timestamp"] > database_list[k][4]:
                    #updates the timestamp in the database for the summoner in question
                    cursor.execute("UPDATE boost_check SET timestamp = ? WHERE summoner_name = ?", [game_idJSON.json()["matches"][0]["timestamp"], database_list[k][0]])
                    db.commit()

                    new_game_id = game_idJSON.json()["matches"][0]["gameId"]
                    new_game_champion_id = game_idJSON.json()["matches"][0]["champion"]
                    new_game_match_dataJSON = requests.get("https://na1.api.riotgames.com/lol/match/v4/matches/" + str(new_game_id) + "?api_key=" + config.RIOT_API_KEY)
                    

                    #parses through stats of every summoner in the game to find the desired summoner
                    for i in range(10):
                        if new_game_match_dataJSON.json()["participants"][i]["championId"] == new_game_champion_id:
                            if new_game_match_dataJSON.json()["participants"][i]["stats"]["win"] == True:
                                team_ID = new_game_match_dataJSON.json()["participants"][i]["teamId"]
                                boosted_score = boosted_score_calculator(new_game_match_dataJSON, i, team_ID)

                                #finds data regarding current boosted score and number of games analyzed
                                #connects to the boost_check database
                                db = sqlite3.connect(BOOST_CHECKER_DIR_PATH)
                                cursor = db.cursor()
                                cursor.execute("SELECT current_boosted_score from boost_check where summoner_name = ?", [database_list[k][0]])
                                current_boosted_score = cursor.fetchone()
                                cursor.execute("SELECT number_of_games_analyzed from boost_check where summoner_name = ?", [database_list[k][0]])
                                number_of_games = cursor.fetchone()
                                #calculates updated versions of this data
                                new_number_of_games = number_of_games[0] + 1
                                new_boosted_score = round(((current_boosted_score[0] * number_of_games[0]) + boosted_score) / (new_number_of_games), 2)

                                #updates the database
                                cursor.execute("UPDATE boost_check SET current_boosted_score = ? where summoner_name = ?", [new_boosted_score, database_list[k][0]])
                                cursor.execute("UPDATE boost_check SET number_of_games_analyzed = ? where summoner_name = ?", [new_number_of_games, database_list[k][0]])
                                db.commit()
                                db.close()

                                await boosted_bot_channel.send(database_list[k][0] + " just won a game, with a boosted score of " + str(boosted_score) + "!")
                            
                            else:
                                await boosted_bot_channel.send(database_list[k][0] + " just lost another game! LOLOLOLOLOLOL")

                            print("successfully detected and analyzed a summoner in boost_check")
                            break

                    
            except Exception as e:
                print(e)

        #once at the end of the loop, the list from the database is updated
        db.close()
        
        #following a conservative rate limit of 75requests/2mins, the wait can be calculated as follows:
        if database_list_length > 0:
            wait_time = 120 / (75/database_list_length)

        else:
            #1.6s/request = 75requests/120seconds < 100requests/120seconds cap of RIOT API (leaves leeway for other requests)
            wait_time = 1.6

        await asyncio.sleep(wait_time)
        
        db.close()
        #once at the end of the loop, the list from the database is updated



#command to find current rank of given NA summoner
@bot.command(name = "rank", help = "Find the current rank of an NA summoner")
async def ranked_stats(ctx, *, league_name):
    try:
        idJSON = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + league_name + "?api_key=" + config.RIOT_API_KEY)
        summoner_id = idJSON.json()["id"]
        ranked_dataJSON = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summoner_id + "?api_key=" + config.RIOT_API_KEY)
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



@bot.command(name = "boosted_add", help = "Add an NA summoner to the boosted checker")
async def boosted_list_adder(ctx, *, league_name):
    #connects to the boost_check database
    db = sqlite3.connect(BOOST_CHECKER_DIR_PATH)
    cursor = db.cursor()

    #checks if summmoner is already in database
    cursor.execute("SELECT * FROM boost_check WHERE summoner_name = ?", [league_name])
    if cursor.fetchone() == None:
        #checks if is a real NA summoner and finds account id
        try:
            idJSON = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + league_name + "?api_key=" + config.RIOT_API_KEY)
            account_id = idJSON.json()["accountId"]        

        except Exception as e:
            print(e)
            await ctx.channel.send("YOU ARE GAPPED! THAT IS NOT A LEGIT NA SUMMONER :<<<<")

            db.close()
            #stops execution of this function if not real summoner
            return
        
        try:
            timestamp = most_recent_timestamp_finder(account_id)

        except Exception as e:
            print(e)
            await ctx.channel.send("BOOSTED BOT IS INTING! COULD NOT FIND SUMMONER'S MOST RECENT GAME'S TIMESTAMP")

            db.close()
            #stops execution of this function if could not find timestamp
            return
        
        cursor.execute("INSERT INTO boost_check VALUES (?, ?, ?, ?, ?)", [league_name, account_id, 0, 0, timestamp])
        db.commit()
        db.close()
        await ctx.channel.send("I HAVE ADDED " + league_name + " TO THE BOOSTED CHECKER! B E W A R E")
    else:
        db.close()
        await ctx.channel.send("THIS SUMMONER IS ALREADY ADDED. INTING INTING!!!")



@bot.command(name = "boosted_remove", help = "Use to remove a summoner from the boosted checker, WOOS!")
async def boosted_list_remover(ctx, *, league_name):
    #connects to the boost_check database
    db = sqlite3.connect(BOOST_CHECKER_DIR_PATH)
    cursor = db.cursor()

    #checks if summmoner is already in database
    cursor.execute("SELECT * FROM boost_check WHERE summoner_name = ?", [league_name])

    #checks if summoner is in the boosted checker
    if cursor.fetchone() == None:
        await ctx.channel.send("THIS SUMMONER IS NOT IN THE BOOSTED CHECKER. BRAIN DIFF ?????")
        db.close()

    else:
        cursor.execute("DELETE FROM boost_check WHERE summoner_name = ?", [league_name])
        db.commit()
        db.close()
        await ctx.channel.send(league_name + " WAS REMOVED FROM THE BOOSTED CHECKER. W O O S!")



#command to see the boosted leaderboard
@bot.command(name = "leaderboard", help = "Reveals the boosted leaderboard")
async def boosted_leaderboard(ctx):
    #connects to the boost_check database
    db = sqlite3.connect(BOOST_CHECKER_DIR_PATH)
    cursor = db.cursor()

    #checks if anyone is in the database 
    cursor.execute("SELECT * FROM boost_check")
    if cursor.fetchall() == []:
        await ctx.channel.send("NO ONE IS IS IN THE BOOST CHECKER YET, B-BAKA!")
    
    else:

        cursor.execute("SELECT summoner_name, number_of_games_analyzed, current_boosted_score FROM boost_check ORDER BY current_boosted_score DESC")
        leaderboard_list = cursor.fetchall()
        db.close()

        #makes title
        embed = discord.Embed(title = "Boosted Leaderboard")
    
        #makes summoner name column 
        summoner_name_section = ""
        for k in range(len(leaderboard_list)):
            summoner_name_section += leaderboard_list[k][0] + "\n"

        embed.add_field(name = "Summoner Name", value = summoner_name_section, inline = True)

        #makes number of games analyzed column
        number_of_games_analyzed_section = ""
        for k in range(len(leaderboard_list)):
            number_of_games_analyzed_section += str(leaderboard_list[k][1]) + "\n"
    
        embed.add_field(name = "# of Games Analyzed", value = number_of_games_analyzed_section, inline = True)

        #makes boosted score column
        boosted_score_section = ""
        for k in range(len(leaderboard_list)):
            boosted_score_section += str(leaderboard_list[k][2]) + "\n"
    
        embed.add_field(name = "Average Boosted Score", value = boosted_score_section, inline = True)

        await ctx.channel.send(embed = embed)



@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(name = "FINDING THE MOST BOOSTED SWINE", type = 5))

    #creates the output channel for the bot
    boosted_bot_channel = bot.get_channel(config.BOOSTED_BOT_CHANNEL_ID)

    #creates boost_check database if not already existing 
    db = sqlite3.connect(BOOST_CHECKER_DIR_PATH)
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boost_check(
        summoner_name TEXT,
        account_id TEXT,
        current_boosted_score REAL,
        number_of_games_analyzed INTEGER,
        timestamp INTEGER 
        )
            """)
    db.commit()

    #updates most recent timestamps in database on startup
    cursor.execute("SELECT * FROM boost_check")
    database_list = cursor.fetchall()
    database_list_length = len(database_list)
    for k in range(database_list_length):
        updated_timestamp = most_recent_timestamp_finder(database_list[k][1])
        cursor.execute("UPDATE boost_check SET timestamp = ? WHERE summoner_name = ?", (updated_timestamp, database_list[k][0]))
        db.commit()

    db.close()

    #adds the game checking loop into the event loop
    bot.loop.create_task(recent_game_loop(boosted_bot_channel))

    #prints in terminal
    print("BOOSTED BOT IS ONLINE")

#connects the bot to discord and creates the event loop (bot)
bot.run(config.DISCORD_API_KEY)
