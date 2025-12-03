import discord
#from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

import gspread
from google.oauth2.service_account import Credentials

# ---------- Intents ----------
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="'", intents=intents)

# ---------- Load environment ----------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COUNCIL_ROLE_ID = os.getenv("COUNCIL_ROLE_ID")
BACKROOM_SHEET_ID = os.getenv("BACKROOM_SHEET_ID")
TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID"))  # for instant slash command sync

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

backroom_page = client.open_by_key(BACKROOM_SHEET_ID)


class Track:
    def __init__(self, row_index, row_data):
        self.name = row_data[0]
        self.authors = row_data[1]
        self.ver = row_data[2]

        # Extract URL from =HYPERLINK("url","label")
        formula = row_data[3]
        self.link = formula.split('"')[1] if formula and "HYPERLINK" in formula else None


# ---------- File check ----------
def check_files():
    if not os.path.exists(".env"):
        print("Missing .env file")
        return False
    if not os.path.exists("council.json"):
        print("Missing council.json")
        return False
    return True

if not check_files():
    print("Error: Required files missing. Exiting...")
    exit(1)

# ---------- Slash commands ----------

@bot.tree.command(name="get_user_info", description="Gets information about a user.")
async def get_user_info(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title="User Information", color=discord.Color.blue())
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="Discriminator", value=user.discriminator, inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="initialise_council", description="Rebuild the council json.")
async def initialise_council(interaction: discord.Interaction):
    council_data = {}
    for user in interaction.guild.members:
        if any(role.name == "Track Council" for role in user.roles):
            council_data[user.id] = {
                "user_name": user.name,
                "user_id": user.id,
                "role": "council"
            }
            if any(role.name.lower() == "admin" for role in user.roles):
                council_data[user.id]["role"] = "admin"

    with open("council.json", "w") as f:
        json.dump(council_data, f, indent=4)

    await interaction.response.send_message("Council JSON rebuilt.")


offset = 3
tracks_in_update = 9

start_row = offset + 1
end_row   = offset + tracks_in_update + 1

@bot.tree.command(name="updates", description="Show Backrooms track list")
async def updates(interaction: discord.Interaction):

    sheet = backroom_page.worksheet("Update Queue")
    data = sheet.get(f"C{start_row}:F{end_row}", value_render_option="FORMULA")


    # Build track objects
    tracks = []
    for i, row in enumerate(data):
        track = Track(i + 1, row)
        print(row)
        tracks.append(track)

    embed = discord.Embed(color=discord.Color.blue())

    for track in tracks:
        field_value = (
            f"**by: ** {track.authors}\n"
            f"v{track.ver}\n"
            f"[Link]({track.link})"
        )

        embed.add_field(
            name=track.name,
            value=field_value,
            inline=False
        )

    await interaction.response.send_message(embed=embed)

# ---------- Events ----------

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    guild = discord.Object(id=TEST_GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("Slash commands synced in test guild!")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        command_name = interaction.data.get("name")
        user = interaction.user
        guild = interaction.guild
        print(f"[COMMAND] {guild} - {user} used /{command_name}")

# ---------- Run ----------
bot.run(DISCORD_TOKEN)
