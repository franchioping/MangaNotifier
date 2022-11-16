import json
import os

from manga import Manga
fileName = os.path.dirname(os.path.realpath(__file__)) + "/util.json"


def read_json():
    with open(fileName, "r") as f:
        return json.load(f)


def write_json(to_write: dict):
    with open(fileName, "w") as f:
        json.dump(to_write, f, indent=3)


def manga_reader_to_obj(manga_reader: Manga):
    ret = {"name": manga_reader.get_name(), "url": manga_reader.get_anime_url(),
           "img_url": manga_reader.get_img_url(), "channel_id": manga_reader.channel, "role_id": manga_reader.role_id}
    return ret


def obj_to_manga_reader(obj: dict) -> Manga:
    return Manga(int(obj["channel_id"]), int(obj["role_id"]), obj["name"], obj["url"],
                                 obj["img_url"])


def add_obj_to_file(obj: dict):
    file = read_json()
    file["manga"].append(obj)
    write_json(file)


def get_name_index(name: str) -> int:
    manga_list = read_json()["manga"]
    for i in range(len(manga_list)):
        if manga_list[i]["name"] == name:
            return i

    return -1


def remove_manga(index: int):
    file = read_json()
    manga_list = file["manga"]
    manga_list.pop(1)
    write_json(file)


def get_manga_names() -> list[str]:
    manga_list = read_json()["manga"]
    ret = []
    for i in manga_list:
        ret.append(i["name"])
    return ret


