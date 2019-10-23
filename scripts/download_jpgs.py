#!/usr/bin/env python

from urllib import request
from bs4 import BeautifulSoup # type: ignore
from http.client import HTTPResponse
import os
from pathlib import Path
from sys import stdout
from typing import List

from prefect import task, Flow

DIREC = 'adl-jpgs' # should be an env var.
FILES_DIR = 'files'
# if not Path(f'files/{DIREC}').is_dir():
#    os.mkdir(DIREC) # a bash script does this now.
   
def make_soup(page_num: int) -> BeautifulSoup:
    html = request.urlopen(
        f"https://www.adl.org/hate-symbols?page={page_num}"
    )
    return BeautifulSoup(html, features='html.parser')

def get_urls(soup: BeautifulSoup) -> List[str]:
    wrapped_imgs = soup.find_all('div', {'class': 'teaser-image'})

    return (wrapped_img.contents[1].contents[2].contents[0].get("src")
            for wrapped_img
            in wrapped_imgs)

def download_image(image: str, counter: int) -> None:
    print(f"now retrieving the {counter:04d}th image...")
    request.urlretrieve(
        image,
        f"{FILES_DIR}/{DIREC}/hate-symbols-db-{counter:04d}.jpg"
    )
    pass

@task
def download_page_of_images(page: int) -> None:

    soup = make_soup(page)

    image_urls = get_urls(soup)

    M = 40

    for j, image in enumerate(image_urls):
        download_image(image, M * page + j)
    None


with Flow("download jpgs") as flow:

    x = download_page_of_images.map(range(6))

    state = flow.run()
