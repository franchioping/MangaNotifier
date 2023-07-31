import json
import os
import sys

from manga import Manga

fileName = os.path.dirname(os.path.realpath(__file__)) + "/util.json"


def init():
    if not os.path.isfile(fileName):
        write_json({"manga_category_id": "", "manga": []})
    try:
        get_manga_category_id()
    except KeyError:
        print("ERROR: add manga_category_id to util.json!")
        exit(-1)

    try:
        get_reaction_role_message_id()
    except KeyError:
        print("ERROR: add get_reaction_role_message_id to util.json!")
        exit(-1)


def read_json():
    with open(fileName, "r") as f:
        return json.load(f)


def write_json(to_write: dict):
    with open(fileName, "w") as f:
        json.dump(to_write, f, indent=3)


def get_manga_category_id() -> int:
    return int(read_json()["manga_category_id"])


def get_reaction_role_message_id() -> int:
    return int(read_json()["reaction_role_message_id"])


def manga_reader_to_obj(manga_reader: Manga):
    ret = {"name": manga_reader.get_name(), "url": manga_reader.get_anime_url(),
           "img_url": manga_reader.get_img_url(), "channel_id": manga_reader.channel, "role_id": manga_reader.role_id,
           "broken": manga_reader.broken}
    return ret


def obj_to_manga_reader(obj: dict) -> Manga:
    if obj.keys().__contains__("broken"):
        return Manga(int(obj["channel_id"]), int(obj["role_id"]), obj["name"], obj["url"],
                     obj["img_url"], obj["broken"])
    else:
        return Manga(int(obj["channel_id"]), int(obj["role_id"]), obj["name"], obj["url"],
                     obj["img_url"], False)


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
    manga_list.pop(index)
    write_json(file)


def get_manga_names() -> list[str]:
    manga_list = read_json()["manga"]
    ret = []
    for i in manga_list:
        ret.append(i["name"])
    return ret


if __name__ == "__main__":
    init()
