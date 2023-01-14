import discord
import os
import cloudscraper as cld


import requests as r


class Manga:

    def __init__(self, channel, role, name, anime_url, image_url):
        self.scraper = cld.create_scraper()
        self.name = name
        self.image_url = image_url
        self.channel = int(channel)
        self.role_id = int(role)
        self.filePath = os.path.dirname(os.path.realpath(__file__)) + "/" + name + ".txt"
        self.anime_url = anime_url
        self.url_ep_str = "%EP%"
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
                              url=self.anime_url.replace(self.url_ep_str, str(ep)),
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

    def get_anime_url(self) -> str:
        return self.anime_url

    def get_img_url(self) -> str:
        return self.image_url

    def get_latest_episode(self):
        print("latest_ep")
        latest_ep = self.get_old_latest_ep()

        if self.check_if_episode_exists(latest_ep) is None:
            return -1

        steps = [100, 50, 10, 1]
        i = 0

        while True:
            exists = self.check_if_episode_exists(latest_ep + steps[i])
            if exists is None:
                return -1
            if exists:
                latest_ep += steps[i]
            else:
                i += 1
                if i > len(steps) - 1:
                    break

        self.set_last_latest_ep(latest_ep)
        return latest_ep

    def check_if_episode_exists(self, num: int):
        req = self.scraper.get(self.anime_url.replace(self.url_ep_str, str(num)))

        if req.status_code == 502:
            return None

        if req.status_code < 200 or req.status_code > 300:
            return False

        # Needed for Rent-a-Girlfriend
        if req.text.count("This is an Upcoming Post.") > 0:
            return False

        return req.text.count("404") == 0
