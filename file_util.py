import json

import manga_reader_to

fileName = "util.json"


def read_json():
    with open(fileName, "r") as f:
        return json.load(f)


def write_json(to_write: dict):
    with open(fileName, "w") as f:
        json.dump(to_write, f, indent=3)


def manga_reader_to_obj(manga_reader: manga_reader_to.MangaReaderAnime):
    ret = {"name": manga_reader.get_name(), "url_end": manga_reader.get_anime_url_end(),
           "img_url": manga_reader.get_img_url(), "channel_id": manga_reader.channel, "role_id": manga_reader.role_id}
    return ret


def obj_to_manga_reader(obj: dict) -> manga_reader_to.MangaReaderAnime:
    return manga_reader_to.MangaReaderAnime(int(obj["channel_id"]), int(obj["role_id"]), obj["name"], obj["url_end"],
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


