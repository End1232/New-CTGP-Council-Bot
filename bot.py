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
    # .env
    if not os.path.exists(".env"):
        print("No environment found - Please ensure the file '.env' exists in the same folder as 'bot.py'")
        return False
    
    # council.json
    if not os.path.exists("council.json"):
        print("No council.json found - Please ensure the file 'council.json' exists in the same folder as 'bot.py'")
        return False
    
    return True

@bot.tree.command(name="echo", description="Echoes a message.")
@app_commands.describe(message="The message to echo.")
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="get_user_info", description="Gets information about a user.")
#@app_commands.describe(user="The user to get information about.")
async def get_user_info(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title="User Information", color=discord.Color.blue())
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="Discriminator", value=user.discriminator, inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="initialise_council", description="Rewrite the council json.")
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

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.tree.sync()  # sync slash commands
    print("Slash commands synced.")

bot.run(DISCORD_TOKEN)
