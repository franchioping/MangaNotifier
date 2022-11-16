import discord

import file_util
import manga_reader_to

from discord.ext import commands
from discord.ext import tasks

from time import gmtime, strftime

token = "MTAzNDE4Njg1MjY3NDA1MjE5Nw.Gvmphf.xH1M7h8HE5RGDJeX0vLbLxEk4daJbVKc0Lbznw"
guild_id = 1042133536926347324

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

manga = []


def get_channel_id_from_mention(mention: str) -> int:
    return int(mention.replace("#", "").replace("<", "").replace(">", ""))


def get_role_id_from_mention(mention: str) -> int:
    return int(mention.replace("@&", "").replace("<", "").replace(">", ""))


@tasks.loop(seconds=10)
async def test():
    guild = bot.get_guild(guild_id)
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
    for i in file_util.read_json()["manga"]:
        manga.append(file_util.obj_to_manga_reader(i))
    test.start()


"""
    argument 0 : anime name, basic ascii only, used in paths
    argument 1 : manga reader url name, for example: chainsaw-man-colored-edition-56074
    argument 2 : image url
    argument 3 : channel where to post updates
    argument 4 : role to ping
"""


@bot.command()
async def add_manga_reader(ctx: discord.ext.commands.Context, *args):
    if len(args) != 5:
        await ctx.send("wrong usage, check source code loser")

    global manga

    manga_reader = manga_reader_to.MangaReaderAnime(get_channel_id_from_mention(args[3]),
                                                    get_role_id_from_mention(args[4]), args[0], args[1], args[2])

    file_util.add_obj_to_file(file_util.manga_reader_to_obj(manga_reader))
    manga.append(manga_reader)
    await ctx.send("success")


@bot.command()
async def list_manga(ctx: discord.ext.commands.Context):
    await ctx.send(str(file_util.get_manga_names()))


@bot.command()
async def remove_manga(ctx: discord.ext.commands.Context, arg):
    index = file_util.get_name_index(arg)
    if index == -1:
        await ctx.send("no manga with than name in use")
        return
    file_util.remove_manga(index)


bot.run(token)
