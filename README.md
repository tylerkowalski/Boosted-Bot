# Boosted-Bot

A Discord bot for League of Legends players in NA. Boosted Bot uses Riot's API and a local database to provide analysis on how boosted an NA summoner is. The bot allows users to find ranked stats through discord commands, sends a message when a summoner in question has won/loss a game, and stores summoner's boosted scores locally to provide insight as to who is the most boosted out of your friends.

## Installation
*It is assumed that you have a Discord account, and the lastet version of Python installed on your computer*

### Setting up Boosted Bot Locally
 1. Download this repository
 2. Make a new text document in the root directory and then type the following with the paths on your machine:
    ![image](https://user-images.githubusercontent.com/83722101/125105647-ae684d80-e0ac-11eb-97f5-18d60ca51a4b.png)
3. Save the file as *start.bat*
4. Delete the *text document*

### Setting up Discord's API to work with your locally run Boosted Bot. 

  1. Log into [Discord's Developer Portal](http://discordapp.com/developers/applications), select *New Application*, name it **BOOSTED DETECTOR**, or whatever you would like, and click *create*
  2. Set the App Icon to boosted_bot_icon.png in \resources  
  3. Go to the *Settings* bar on the left, and scroll to *Bot*
  4. Click *Add Bot*, and then proceed to set the bot icon to boosted_bot_icon.png and the username **BOOSTED bot** *(you can always use whatever names or images you would like)*
  5. Copy the Token and insert it in the quotation marks after *DISCORD_API_KEY=* in \src\config.py (you will need to open and edit this python file)
  6. Go to *OAuth2* on the *Settings* bar, add the scope *bot*, and then ***at least*** add the permission *Send Messages*. I recommend giving in *Administrator  in case I, or you, wish to add more functionality to the bot later
  7. Copy the URL generated and paste it into your browser. 
  8. Select the server you wish to add the bot in, then click *Authorize*

### Getting a Riot API Token
In order to get League of Legends Data, you will need a Riot API token. 
  1. Log into [Riot's Developer  Portal](https://developer.riotgames.com) using your Riot account
  2. Copy the *Development API Key* into the quotation marks after *RIOT_API_KEY=* in \src\config.py
  
*I recommend applying for Personal API Key by registering this bot with Riot Games because otherwise, you would need to get a new API key every 24 hours*
 
 ### Setting the Boosted Channel
 One of the bot's features is to send a message whenever a summoner you added to *boost_check* (more on that below) has played a ranked game. To set the channel that you wish the bot to output this message to, do the following:
 1. Log into Discord, go into *User Settings* (the cog symbol), *Advanced*, and then turn on *Developer Mode*
 2. Right click on the channel you wish the bot to send game messages to, then click *Copy Id*
 3. Paste the ID after *BOOSTED_BOT_CHANNEL_ID=* in \src\config.py (it is important that the channel id is not in quotations)

## Usage
 Boosted Bot has many uses. Here are the different features:
 
 
 ### ?rank
 This command returns the ranked stats of any NA summoner this season (11). It can be used as follows:
 ![image](https://user-images.githubusercontent.com/83722101/125109245-1b7de200-e0b1-11eb-83c2-f4e28c105b2e.png)


### boost_check
boost_check is the local database which stores the summoners you wish Boosted Bot to provide updates on their recent ranked games. After a summoner in boost_check plays a ranked game, Boosted Bot will send a message to the *Boosted Channel* with information about that game. If it was a win, a boosted score will also be given and will be stored in the database. For example:
![image](https://user-images.githubusercontent.com/83722101/125110276-5f251b80-e0b2-11eb-9a77-ee3ab36f8a6f.png)
*Note that Riot takes 3-5 mins after a game to update the database which the Riot API we are using, uses*

*Note that a Boosted Score is only given when the summoner has won, since it is a measure of the summoner's imapct in their win*


### Boosted Score
A summoner's Boosted Score is only calculated when the summoner in question has won a game, since it is a measure of the summoner's impact in their win. The way it is calcualted, a positive Boosted Score means that summoner was boosted that game, having less of an impact than the average summoner on their team. A negative Boosted Scores means the opposite; the summoner was carrying that game, having more of an impact than the average summoner on their team.

### ?leaderboard
This command returns the *Boosted Leaderboard*, organized from most to least boosted. Here is the output in my server as of 07/09/2021:
![image](https://user-images.githubusercontent.com/83722101/125111279-b677bb80-e0b3-11eb-84ba-decd1a139956.png)


### ?boosted_add
This command adds any NA summoner to the boost_check database. It can be used as follows:
![image](https://user-images.githubusercontent.com/83722101/125111688-33a33080-e0b4-11eb-8464-fba2c5c55ac3.png)


### ?boosted_remove
This command removes any summoner currently in the boost_check database. It can be used as follows:
![image](https://user-images.githubusercontent.com/83722101/125111593-179f8f00-e0b4-11eb-8238-156d77aeb644.png)


 
