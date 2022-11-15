import discord

import rent_a_girlfriend
import manga_reader_to

from discord.ext import commands
from discord.ext import tasks

from time import gmtime, strftime

token = "MTA0MjEzNDEzMTE3MTEzMTQ3Mw.GcXpnu.631JcY67ArGM8xv8XUkp3fDHICgVYGvGjb0y6E"
guild_id = 1034187527751479427

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

manga = []


@tasks.loop(seconds=60)
async def test():
    guild = bot.get_guild(guild_id)
    time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    for i in manga:
        if int(i.get_old_latest_ep()) != int(i.get_latest_episode()):
            episode = i.get_latest_chapter()
            embed = i.get_embed(time_str, episode)
            role = guild.get_role(i.get_role_id())
            await bot.get_channel(i.get_channel()).send(embed=embed, content=role.mention,
                                                        allowed_mentions=discord.AllowedMentions(everyone=True))
            i.set_last_latest_ep(episode)


@bot.event
async def on_ready():
    test.start()


manga.append(rent_a_girlfriend.RentAGirlfriend(1042146239795441724, 1042145017239719958))
manga.append(manga_reader_to.MangaReaderAnime(1042146295420289054, 1042145333922250762, "Chainsaw_Man", "chainsaw-man-96", "https://cdn.readheroacademia.com/file/CDN-M-A-N/chain.jpg"))



bot.run(token)
