import discord
import os
import cloudscraper as cld
import sys


class Manga:
    def __init__(self, channel: int, role: int, name: str, url: str, image_url: str, broken: bool):
        self.scraper = cld.create_scraper()
        self.channel_id = channel
        self.role_id = role
        self.name = name
        self.image_url = image_url
        self.broken = broken

        url_delim = "||"

        self.url_ep_str = "%EP%"

        self.urls = url.split(url_delim)

        self.filePath = os.path.dirname(os.path.realpath(__file__)) + "/" + name + ".txt"
        open(self.filePath, "a+").close()

        for x in self.urls:
            if x.count("%EP%") == 0:
                print(self.name, " - URL is Probably Incorrect - ", x, file=sys.stderr)

        self.steps = [100, 50, 10, 5, 1]
        self.i = 0
        if self.get_old_latest_chapter() > 1:
            self.i = len(self.steps) - 2

    def get_embed(self, time_str: str, ep: int, url):
        embed = discord.Embed(title=f"New Chapter Of {self.name} Manga",
                              url=url.replace(self.url_ep_str, str(ep)),
                              description=f"Chapter {ep} just dropped at {time_str} GMT",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=self.image_url)

        return embed

    def set_last_latest_chapter(self, ep: int):
        with open(self.filePath, "w") as f:
            f.write(str(ep))

    def get_old_latest_chapter(self) -> int:
        with open(self.filePath, "r") as f:
            try:
                num = int(f.readline())
                if num > 0:
                    return num
                else:
                    raise ValueError
            except ValueError:
                print("File is empty")
                self.set_last_latest_chapter(1)
                return 1

    def get_latest_chapter(self):
        print(" - Attempting Requests on ", self.urls)
        latest_ep = self.get_old_latest_chapter()

        if self.check_if_chapter_exists(latest_ep) is None:
            return -1

        steps = self.steps
        url = ""

        while True:
            resp = self.check_if_chapter_exists(latest_ep + steps[self.i])
            exists = resp[0]
            if exists is None:
                return -1
            if exists:
                latest_ep += steps[self.i]
            else:
                url = resp[1]
                if self.i == -1:
                    break
                self.i += 1
                if self.i > len(steps) - 1:
                    self.i = -1
                    break

        self.set_last_latest_chapter(latest_ep)
        return [latest_ep, url]

    def check_if_chapter_exists(self, num):
        offline = 0

        for url in self.urls:
            req = self.scraper.get(url.replace(self.url_ep_str, str(num)))
            print(f"  -- Chap {num} on URL {url} HTTP GET Result: ", req.status_code)

            if req.status_code < 200 or req.status_code > 300:
                continue

            if req.status_code == 502:
                print("   --- Code 502 - Server May be Offline")
                offline += 1
                continue

            # Needed for Rent-a-Girlfriend
            if req.text.count("This is an Upcoming Post.") > 0:
                print("   --- Not released yet - Upcoming Post")
                continue

            # Needed for https://mangakakalot.com/
            if req.text.count("Sorry, the page you have requested cannot be found.") > 0:
                print("   --- Not released yet - Page cannot be found")
                continue

            if sum([url.count(x) for x in ["www.blueboxmanga.com", "kanojo-okarishimasu-manga.com"]]):

                if sum([int(i.status_code < 200 or i.status_code > 300) for i in req.history]):
                    print("   --- Failed on History")
                    continue

            return [True, url]

        return [None, ""] if offline else [False, ""]
