import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="'", intents=intents)

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COUNCIL_ID = 1444154602340614306


"""
Ensure all required files are present - 
<private> .env - Contains bot token
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
    

@bot.event
async def on_ready():
    print("Bot is ready")
    await bot.tree.sync()  # sync slash commands
    print("Slash commands synced.")

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


bot.run(DISCORD_TOKEN)
