import os
import sys

import discord
from dotenv import load_dotenv

import file_util
from manga import Manga

from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
import manga_reader_util

import asyncio

from time import gmtime, strftime

load_dotenv()

token = os.getenv("TOKEN")
guild_id = int(os.getenv("GUILD"))
delay = int(os.getenv("DELAY"))

assert guild_id is not None
assert token is not None
assert delay is not None

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

manga: list[Manga] = []
manga_category: discord.CategoryChannel


def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)


def get_channel_id_from_mention(mention: str) -> int:
    return int(mention.replace("#", "").replace("<", "").replace(">", ""))


def get_role_id_from_mention(mention: str) -> int:
    return int(mention.replace("@&", "").replace("<", "").replace(">", ""))


@tasks.loop(seconds=delay)
async def check_chapter_loop():
    guild = bot.get_guild(guild_id)
    time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    gmt_time = gmtime()
    if gmt_time.tm_hour != 23 or gmt_time.tm_min > 15:
        print(f"Starting Checks At {time_str}")
        for i in manga:
            print(f"=== Starting {i.name} Check ===")
            await asyncio.sleep(1)
            was_broken = i.broken
            old_latest_ep = int(i.get_old_latest_ep())
            latest_ep = i.get_latest_episode()
            is_broken = i.broken
            print(" - Latest EP: ", str(latest_ep), " Old Latest EP: ", old_latest_ep)
            if latest_ep == -1:
                print(f"ERROR - Web Request to " + str(i.anime_url) + " Failed.", file=sys.stderr)
                continue

            if was_broken == False and is_broken == True:
                print(i.name, ' - Manga is Broken, Sending Alert')
                role = guild.get_role(i.get_role_id())
                msg = """
                Hey Everyone, This Manga is broken, contact the server owned to know why
                The site probably implemented anit-scraping features, so now its harder to have a bot check if theres a new chapter
                If you find another site that has this manga, send it over on bug-reports and ill fix it
                
                """
                await bot.get_channel(i.get_channel()).send(msg + role.mention, allowed_mentions=discord.AllowedMentions(everyone=True))

            if old_latest_ep != latest_ep:
                print(i.name, " - There's a new EP, Sending Notification")
                episode = i.get_latest_chapter()
                embed = i.get_embed(time_str, episode)
                role = guild.get_role(i.get_role_id())
                await bot.get_channel(i.get_channel()).send(embed=embed, content=role.mention,
                                                            allowed_mentions=discord.AllowedMentions(everyone=True))
                i.set_last_latest_ep(episode)
    else:
        print(f"ERROR - Server is within reboot time, aborting", file=sys.stderr)


@bot.event
async def on_ready():
    file_util.init()
    for i in file_util.read_json()["manga"]:
        manga.append(file_util.obj_to_manga_reader(i))
    global manga_category
    manga_category = discord.utils.get(bot.get_guild(guild_id).categories, id=int(file_util.get_manga_category_id()))
    check_chapter_loop.start()


def add_manga(channel_id: int, role_id: int, public_name: str, url: str, img_url: str):
    manga_reader = Manga(channel_id,
                         role_id, public_name, url, img_url)

    file_util.add_obj_to_file(file_util.manga_reader_to_obj(manga_reader))
    manga.append(manga_reader)


async def add_quick_manga(name: str, chap_url: str,
                    img_url: str = "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg?20200913095930") -> None:
    everyone = bot.get_guild(guild_id).default_role

    channel = await bot.get_guild(guild_id).create_text_channel(name, category=manga_category)
    notification_role = await bot.get_guild(guild_id).create_role(name=name)
    await channel.set_permissions(everyone,
                                  overwrite=discord.PermissionOverwrite(send_messages=False, view_channel=False))
    await channel.set_permissions(notification_role, overwrite=discord.PermissionOverwrite(view_channel=True))

    add_manga(channel.id, notification_role.id, name, chap_url, img_url)


def gen_reaction_role_command(name: str, emoji: str):
    react_role_msg_id = file_util.get_reaction_role_message_id()

    role_id = file_util.read_json()["manga"][file_util.get_name_index(name)]["role_id"]
    role_mention = bot.get_guild(guild_id).get_role(role_id).mention
    return f"/reactionrole add message_id:{react_role_msg_id} emoji:{emoji} role:{role_mention}"


async def add_manga_reader(public_name: str, site_name: str):
    img_url = manga_reader_util.get_image_url(site_name)
    chap_url = f"https://mangareader.to/read/{site_name}/en/chapter-%EP%"

    await add_quick_manga(public_name, chap_url, img_url)


@bot.command(name="add_manga")
@commands.check_any(is_guild_owner())
async def add_manga_command(ctx: discord.ext.commands.Context, *args):
    if len(args) != 5:
        await ctx.send("wrong usage, check source code bozo")
        return

    global manga

    add_manga(get_channel_id_from_mention(args[3]),
              get_role_id_from_mention(args[4]), args[0], args[1], args[2])

    await ctx.send("success")


@bot.command(name="add_manga_reader")
@commands.check_any(is_guild_owner())
async def add_manga_reader_command(ctx: discord.ext.commands.Context, *args):
    if len(args) != 2:
        await ctx.send("wrong usage, check source code bozo")
        return
    public_name = str(args[0])
    site_name = str(args[1])

    await add_manga_reader(public_name, site_name)

    await ctx.send("success")


@bot.command()
@commands.check_any(is_guild_owner())
async def add_qm(ctx: discord.ext.commands.Context, *args):
    if len(args) != 3:
        await ctx.send("wrong usage, check source code bozo")
        return

    public_name = str(args[0])
    site_name = str(args[1])
    await add_manga_reader(public_name, site_name)
    await ctx.send(gen_reaction_role_command(public_name, str(args[2])))


@bot.command()
@commands.check_any(is_guild_owner())
async def add_cqm(ctx: discord.ext.commands.Context, *args):
    if len(args) != 3:
        await ctx.send("wrong usage, check source code bozo")
        return

    public_name = str(args[0])
    chap_url = str(args[1])
    await add_quick_manga(public_name, chap_url)
    await ctx.send(gen_reaction_role_command(public_name, str(args[2])))


@bot.command()
@commands.check_any(is_guild_owner())
async def list_manga(ctx: discord.ext.commands.Context):
    await ctx.send(str(file_util.get_manga_names()))


@bot.command()
@commands.check_any(is_guild_owner())
async def remove_manga(ctx: discord.ext.commands.Context, arg):
    index = file_util.get_name_index(arg)
    if index == -1:
        await ctx.send("no manga with than name in use")
        return
    file_util.remove_manga(index)


@bot.command()
@commands.check_any(is_guild_owner())
async def refresh_manga(ctx: discord.ext.commands.Context):
    await check_chapter_loop()
    await ctx.send("success")


bot.run(token)
