import requests as r
from bs4 import BeautifulSoup


def get_image_url(site_name: str) -> str:
    request = r.get("https://mangareader.to/" + site_name)

    html_t = request.text
    html = BeautifulSoup(html_t, features="html.parser")

    manga_img = html.body.find("img", attrs={'class': 'manga-poster-img'})["src"]

    return manga_img


if __name__ == "__main__":
    print(get_image_url("chainsaw-man-colored-edition-56074"))
