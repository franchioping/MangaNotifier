import discord
import os

import requests as r


class MangaReaderAnime:

    def __init__(self, channel, role, name, anime_url_end, image_url):
        self.name = name
        self.image_url = image_url
        self.channel = channel
        self.role_id = role
        self.filePath = os.path.dirname(os.path.realpath(__file__)) + "/" + name + ".txt"
        self.anime_url_end = anime_url_end
        open(self.filePath, "a+").close()

    def set_last_latest_ep(self, ep: int):
        with open(self.filePath, "w") as f:
            f.write(str(ep))

    def get_old_latest_ep(self) -> int:
        with open(self.filePath, "r") as f:
            try:
                return int(f.readline())
            except ValueError:
                self.set_last_latest_ep(1)
                return 1

    def get_latest_chapter(self) -> int:
        return self.get_latest_episode()

    def get_embed(self, time_str: str, ep: int):
        embed = discord.Embed(title=f"New Chapter Of {self.name} Manga",
                              url=f"https://mangareader.to/read/{self.anime_url_end}/en/chapter-{ep}",
                              description=f"Chapter {ep} just dropped at {time_str} GMT",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=self.image_url)

        return embed

    def get_channel(self):
        return self.channel

    def get_role_id(self):
        return self.role_id

    def get_latest_episode(self):
        print("latest_ep")
        latest_ep = self.get_old_latest_ep()
        while not self.check_if_episode_exists(latest_ep):
            print(latest_ep)
            latest_ep += 1

        self.set_last_latest_ep(latest_ep - 1)
        return latest_ep - 1

    def check_if_episode_exists(self, num: int):
        return r.get(f"https://mangareader.to/read/{self.anime_url_end}/en/chapter-{num}").text.count("404") > 0
