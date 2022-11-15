import discord
import os

import requests as r
from bs4 import BeautifulSoup


class RentAGirlfriend:

    def __init__(self, channel, role):
        self.channel = channel
        self.role_id = role
        self.filePath = os.path.dirname(os.path.realpath(__file__)) + "/rent-a-gf.txt"

    def set_last_latest_ep(self, ep: int):
        with open(self.filePath, "w") as f:
            f.write(str(ep))

    def get_old_latest_ep(self):
        with open(self.filePath, "r") as f:
            return f.readline()

    def get_last_listed_episode(self):
        request = r.get("https://kanojo-okarishimasu.com/")

        html_t = request.text

        html = BeautifulSoup(html_t, features="html.parser")

        chap_tab = html.body.find('table', attrs={'class': 'chap_tab'}).text
        cleaned_text = "".join([s for s in chap_tab.strip().splitlines(True) if s.strip()])
        first_line = cleaned_text.partition('\n')[0]
        episode_num = int(first_line.split(" ")[-1])
        return episode_num

    def is_episode_out(self, ep: int):
        request = r.get(f"https://kanojo-okarishimasu.com/manga/rent-a-girlfriend-chapter-{ep}")
        if request.status_code == 200:
            if request.text.count("This is an Upcoming Post.") > 0:
                return False
            return True
        return False

    def get_latest_episode(self):
        last_listed = self.get_last_listed_episode()
        if self.is_episode_out(last_listed):
            return last_listed
        else:
            return last_listed - 1

    def get_latest_chapter(self) -> int:
        return self.get_latest_episode()

    def get_embed(self, time_str: str, ep: int):
        embed = discord.Embed(title="New Chapter Of Rent-a-Girlfriend Manga",
                              url=f"https://kanojo-okarishimasu.com/manga/rent-a-girlfriend-chapter-{ep}",
                              description=f"Chapter {ep} just dropped at {time_str} GMT",
                              color=discord.Color.blue())
        embed.set_thumbnail(url="https://cdn.kanojo-okarishimasu.com/file/CDN-M-A-N/kanojo/Kanojo-Okarishimasu.jpg")

        return embed

    def get_channel(self):
        return self.channel

    def get_role_id(self):
        return self.role_id
