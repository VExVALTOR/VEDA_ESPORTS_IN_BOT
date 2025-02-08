import os
import discord
import random
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load environment variables
load_dotenv("bot_token.env")
TOKEN = os.getenv("DC_TOKEN")
VOICE_CHANNEL_ID = os.getenv("VC_ID")

if not TOKEN:
    raise ValueError("DC_TOKEN not found in environment variables.")
if not VOICE_CHANNEL_ID:
    raise ValueError("VC_ID not found in environment variables.")
try:
    VOICE_CHANNEL_ID = int(VOICE_CHANNEL_ID)
except ValueError:
    raise ValueError("VC_ID must be a valid integer.")

# Set up bot with intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def has_permissions(ctx, perms):
    return all(getattr(ctx.author.guild_permissions, perm, False) for perm in perms)

@tasks.loop(minutes=5)
async def check_voice():
    await connect_to_voice()

async def connect_to_voice():
    try:
        channel = await bot.fetch_channel(VOICE_CHANNEL_ID)
        if isinstance(channel, discord.VoiceChannel):
            for vc in bot.voice_clients:
                if vc.channel.id == VOICE_CHANNEL_ID:
                    return
                else:
                    await vc.disconnect()
            await channel.connect()
            print(f"🔊 Connected to voice channel: {channel.name}")
    except Exception as e:
        print(f"❌ Error connecting to voice: {e}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await connect_to_voice()
    check_voice.start()

@bot.command()
async def mute(ctx, member: discord.Member):
    if not has_permissions(ctx, ["mute_members"]):
        await ctx.send("❌ You don't have permission to mute members!")
        return
    try:
        if not member.voice or not member.voice.channel:
            await ctx.send(f"{member.mention} is not in a voice channel!")
            return
        await member.edit(mute=True)
        await ctx.send(f"🔇 {member.mention} has been muted.")
    except discord.Forbidden:
        await ctx.send("⚠️ I don't have permission to mute members!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def meme(ctx):
    try:
        response = requests.get("https://meme-api.com/gimme", timeout=5)
        data = response.json()
        meme_url = data.get("url", "https://i.imgur.com/placeholder.jpg")
        await ctx.send(f"🤣 Here's a meme for you: {meme_url}")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"⚠️ Error fetching meme: {str(e)}")

@bot.command()
async def fact(ctx):
    facts = [
        "🚀 Did you know honey never spoils?",
        "🐱 Cats have more bones than humans!",
        "🌍 A day on Venus is longer than a year on Venus!"
    ]
    await ctx.send(f"💡 Fun Fact: {random.choice(facts)}")

@bot.command()
async def roast(ctx, member: discord.Member):
    roasts = [
        "🔥 {mention}, you bring everyone so much joy… when you leave the room!",
        "🤣 {mention}, your secrets are safe with me. I never even listen when you tell me them!",
        "😈 {mention}, I’d agree with you but then we’d both be wrong!"
    ]
    await ctx.send(random.choice(roasts).format(mention=member.mention))

@bot.command()
async def bgmi_stats(ctx, player_id):
    url = f"https://api.bgmi-stats.com/{player_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        await ctx.send(
            f"🎯 Player {player_id}: \n📈 KD: {data.get('kd', 'N/A')} \n🏆 Rank: {data.get('rank', 'N/A')}"
        )
    except requests.exceptions.RequestException as e:
        await ctx.send(f"⚠️ Error fetching BGMI stats: {str(e)}")

@bot.command()
async def schedule(ctx):
    scrims = [
        "📅 Monday 8-9-10-11 PM",
        "📅 Tuesday 8-9-10-11 PM",
        "📅 Wednesday 8-9-10-11 PM",
        "📅 Thursday 9-10-11 PM",
        "📅 Friday 8-9-10-11 PM",
        "📅 Saturday 8-9-10-11 PM"
    ]
    await ctx.send(f"🔔 Upcoming scrims: \n" + "\n".join(scrims))

@bot.command()
async def role(ctx, role_name):
    try:
        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
        if role:
            if role >= ctx.me.top_role:
                await ctx.send("❌ This role is higher than my highest role!")
                return
            await ctx.author.add_roles(role)
            await ctx.send(f"✅ {ctx.author.mention}, you now have the {role.name} role! 🔥")
        else:
            await ctx.send("❌ Role not found! Make sure you typed it correctly.")
    except discord.Forbidden:
        await ctx.send("⚠️ I don't have permission to manage roles!")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

bot.run(TOKEN)
