import discord
import os

import requests as r


class MangaReaderAnime:

    def __init__(self, channel, role, name, anime_url_end, image_url):
        self.name = name
        self.image_url = image_url
        self.channel = int(channel)
        self.role_id = int(role)
        self.filePath = os.path.dirname(os.path.realpath(__file__)) + "/" + name + ".txt"
        self.anime_url_end = anime_url_end
        open(self.filePath, "a+").close()

    def set_last_latest_ep(self, ep: int):
        with open(self.filePath, "w") as f:
            f.write(str(ep))

    def get_old_latest_ep(self) -> int:
        with open(self.filePath, "r") as f:
            try:
                num = int(f.readline())
                if num > 0:
                    return num
                else:
                    raise ValueError
            except ValueError:
                print("File is empty")
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

    def get_channel(self) -> int:
        return self.channel

    def get_role_id(self) -> int:
        return self.role_id

    def get_name(self) -> str:
        return self.name

    def get_anime_url_end(self) -> str:
        return self.anime_url_end

    def get_img_url(self) -> str:
        return self.image_url

    def get_latest_episode(self):
        print("latest_ep")
        latest_ep = self.get_old_latest_ep()

        step_size = 5
        while not self.check_if_episode_exists(latest_ep):
            print(latest_ep)
            latest_ep += step_size
        latest_ep -= step_size

        while not self.check_if_episode_exists(latest_ep):
            print(latest_ep)
            latest_ep += 1

        self.set_last_latest_ep(latest_ep - 1)
        return latest_ep - 1

    def check_if_episode_exists(self, num: int):
        return r.get(f"https://mangareader.to/read/{self.anime_url_end}/en/chapter-{num}").text.count("404") > 0
