import os

import discord
from dotenv import load_dotenv

import file_util
from manga import Manga

from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
import manga_reader_util

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

manga = []
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
async def test():
    guild = bot.get_guild(guild_id)
    gmt_time = gmtime()
    if gmt_time.tm_hour != 23 or gmt_time.tm_min > 15:
        time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        for i in manga:
            print("manga")
            if int(i.get_old_latest_ep()) != int(i.get_latest_episode()):
                print("new episode!")
                episode = i.get_latest_chapter()
                embed = i.get_embed(time_str, episode)
                role = guild.get_role(i.get_role_id())
                print("channel" + str(i.get_channel()))
                print("role" + str(i.get_role_id()))
                await bot.get_channel(i.get_channel()).send(embed=embed, content=role.mention,
                                                            allowed_mentions=discord.AllowedMentions(everyone=True))
                i.set_last_latest_ep(episode)


@bot.event
async def on_ready():
    file_util.init()
    for i in file_util.read_json()["manga"]:
        manga.append(file_util.obj_to_manga_reader(i))
    global manga_category
    manga_category = discord.utils.get(bot.get_guild(guild_id).categories, id=int(file_util.get_manga_category_id()))
    test.start()


"""
    argument 0 : anime name, basic ascii only, used in paths
    argument 1 : manga reader url name, for example: chainsaw-man-colored-edition-56074
    argument 2 : image url
    argument 3 : channel where to post updates
    argument 4 : role to ping
"""


def add_manga(channel_id: int, role_id: int, public_name: str, url: str, img_url: str):
    manga_reader = Manga(channel_id,
                         role_id, public_name, url, img_url)

    file_util.add_obj_to_file(file_util.manga_reader_to_obj(manga_reader))
    manga.append(manga_reader)


@bot.command(name="add_manga")
@commands.check_any(is_guild_owner())
async def add_manga_command(ctx: discord.ext.commands.Context, *args):
    if len(args) != 5:
        await ctx.send("wrong usage, check source code bozo")

    global manga

    add_manga(get_channel_id_from_mention(args[3]),
              get_role_id_from_mention(args[4]), args[0], args[1], args[2])

    await ctx.send("success")


async def add_manga_reader(public_name: str, site_name: str):
    img_url = manga_reader_util.get_image_url(site_name)
    chap_url = f"https://mangareader.to/read/{site_name}/en/chapter-%EP%"

    everyone = bot.get_guild(guild_id).default_role

    channel = await bot.get_guild(guild_id).create_text_channel(public_name, category=manga_category)
    notification_role = await bot.get_guild(guild_id).create_role(name=public_name)
    await channel.set_permissions(everyone,
                                  overwrite=discord.PermissionOverwrite(send_messages=False, view_channel=False))
    await channel.set_permissions(notification_role, overwrite=discord.PermissionOverwrite(view_channel=True))

    add_manga(channel.id, notification_role.id, public_name, chap_url, img_url)


@bot.command(name="add_manga_reader")
@commands.check_any(is_guild_owner())
async def add_manga_reader_command(ctx: discord.ext.commands.Context, *args):
    if len(args) != 2:
        await ctx.send("wrong usage, check source code bozo")
    public_name = str(args[0])
    site_name = str(args[1])

    await add_manga_reader(public_name, site_name)

    await ctx.send("success")


@bot.command()
@commands.check_any(is_guild_owner())
async def add_qm(ctx: discord.ext.commands.Context, *args):
    if len(args) != 3:
        await ctx.send("wrong usage, check source code bozo")

    public_name = str(args[0])
    site_name = str(args[1])
    await add_manga_reader(public_name, site_name)

    emoji = str(args[2])
    react_role_msg_id = file_util.get_reaction_role_message_id()

    role_id = file_util.read_json()["manga"][file_util.get_name_index(public_name)]["role_id"]
    role_mention = bot.get_guild(guild_id).get_role(role_id).mention
    await ctx.send(f"/reactionrole add message_id:{react_role_msg_id} emoji:{emoji} role:{role_mention}")


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
    await test()
    await ctx.send("success")


bot.run(token)
