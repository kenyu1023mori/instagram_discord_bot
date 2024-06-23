import discord
from discord.ext import tasks, commands
from instaloader import Instaloader, Profile
from datetime import datetime, time, timedelta
import asyncio
import logging
import sys

# Discord token settings
DISCORD_TOKEN = "YOUR_DISCORD_TOKEN"    # Replace with your Discord bot token
CHANNEL_ID = 123456789012345678    # Replace with your Discord channel ID

# Instaloader settings
L = Instaloader()
PROFILE = "instagram_profile"     # Replace with the Instagram profile you want to monitor


def get_yesterday_posts(profile_name):
    profile = Profile.from_username(L.context, profile_name)
    posts = profile.get_posts()
    yesterday_posts = []
    yesterday = datetime.today() - timedelta(days=1)

    for post in posts:
        if post.date.date() == yesterday.date():
            post_info = {
                "url" : f"https://www.instagram.com/p/{post.shortcode}/",
                "thumbnail_url" : post.url,
                "caption" : post.caption
            }
            yesterday_posts.append(post_info)

    return yesterday_posts

# Discord bot settings
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    if len(sys.argv) != 3:
        print("Usage: python template.py <hour> <minute>")
        return
    try:
        target_hour = int(sys.argv[1])
        target_minute = int(sys.argv[2])
    except ValueError:
        print("Hour and minute should be integers.")
        return

    now = datetime.now()
    target_time = time(target_hour, target_minute)
    first_run = datetime.combine(now.date(), target_time)
    if now > first_run:
        first_run += timedelta(days=1)
        wait_time = (first_run - now).total_seconds()
        await asyncio.sleep(wait_time)
        post_daily.start()

@tasks.loop(hours=24)
async def post_daily():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found, please check ID.")
        return

    try:
        yesterday_posts = get_yesterday_posts(PROFILE)
        if yesterday_posts:
            for post_info in yesterday_posts:
                if len(post_info["caption"]) > 100:
                    truncated_caption = post_info["caption"][:100] + "..."
                else:
                    truncated_caption = post_info["caption"]
                description = f"{truncated_caption}\n[View Post]({post_info['url']})"
                embed = discord.Embed(description=description)
                embed.set_image(url=post_info["thumbnail_url"])
                await channel.send(embed=embed)
        else:
            await channel.send("There was no post yesterday ...")
    except Exception as e:
        print(f"Error occurred: {e}")

bot.run(DISCORD_TOKEN)
