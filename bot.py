import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="'", intents=intents)

"""
Load environment variables from PRIVATE .env file

"""
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COUNCIL_SHEET_ID = os.getenv("COUNCIL_SHEET_ID")
COUNCIL_ROLE_ID = os.getenv("COUNCIL_ROLE_ID")
ADMIN_ROLE_ID = os.getenv("ADMIN_ROLE_ID")
OPERATOR_ROLE_ID = os.getenv("OPERATOR_ROLE_ID")

"""
Ensure all required files are present - 
<private> .env - Contains bot token, council sheet key and other data which should be kept secure
<private> council.json - Contains user IDs and info of council members

"""
def check_files():
    if not os.path.exists(".env"):
        print("No environment found - Please ensure the file '.env' exists in the same folder as 'bot.py'")
        return False
    
    if not os.path.exists("council.json"):
        print("No council.json found - Please ensure the file 'council.json' exists in the same folder as 'bot.py'")
        return False
    
    return True

"""
Slash Commands

"""

"""
TEST COMMAND - Gets information about a user.
Input fields - None (uses interaction user)
Output - Embed containing user information

"""
@bot.tree.command(name="get_user_info", description="Gets information about a user.")
async def get_user_info(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title="User Information", color=discord.Color.blue())
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="Discriminator", value=user.discriminator, inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    await interaction.response.send_message(embed=embed)

"""
<admin> 
Initialises/Rebuilds the private local .json (used for quick response times, run this command whenever new members are added)
    - Will add an auto update feature later, perhaps every 24 hours?

"""
@bot.tree.command(name="initialise_council", description="Rebuild the council json.")
async def initialise_council(interaction: discord.Interaction):
    council_data = {}
    
    for user in interaction.guild.members:
        if any(role.id == "Track Council" for role in user.roles):
            if user.id not in council_data:
                council_data[user.id] = {
                    "user_name" : user.name,
                    "user_id"   : user.id,
                    "role"      : "council"
                }
            
            if any(role.name == "admin" for role in user.roles):
                council_data[user.id]["role"] = "admin"
    
    with open("council.json", "w") as file:
        json.dump(council_data, file, indent=4)

    await interaction.response.send_message("Council JSON Rebuilt.")


"""
Runs every time the bot is restarted, 

"""
@bot.event
async def on_ready():
    check_files() # validate files
    print("Bot is ready")
    await bot.tree.sync()  # sync slash commands
    print("Slash commands synced.")

bot.run(DISCORD_TOKEN)
