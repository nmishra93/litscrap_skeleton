#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from dataclasses import dataclass
import time
import json
import hishel
from selectolax.parser import HTMLParser
from rich import print

URL_LIST = "urls.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


@dataclass
class Page:
    author: str
    story_title: str
    story_blurb: str
    rating: str
    publication_date: str
    story_link: str


@dataclass
class Response:
    body_html: HTMLParser


def read_urls(file: str) -> list:
    with open(file, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def clean_text(text: str) -> str:
    return text.replace("(", "").replace(")", "")


def extract_ratings(authors: list) -> list:
    return [float(author.split("\xa0")[1]) for author in authors]


async def fetch_page_data(url: str, client: hishel.AsyncCacheClient) -> dict:
    response = await client.get(url, headers=HEADERS)
    html = HTMLParser(response.text)

    author_element = html.css_first(".contactheader", default=None)
    author = author_element.text() if author_element else None

    stories = html.css(".fc")
    if stories:
        stories = [story.text() for story in stories]
        story_title = [item.split("\xa0")[0] for item in stories]
        authors = [clean_text(item) for item in stories]
        ratings = extract_ratings(authors)

        story_links = html.css(".fc a")
        link = [link.attributes["href"] for link in story_links]

        blurbs = html.css("div td:nth-child(2)")
        if blurbs:
            blurb = [
                blurb.text().split("\xa0")[0].strip()
                for blurb in blurbs
                if blurb.text().strip()
            ]

            categories = html.css(".r-5 span")
            if categories:
                category = [category.text().strip() for category in categories]

                dates = html.css("div td:nth-child(4)")
                if dates:
                    publication_date = [
                        date.text().strip() for date in dates if date.text().strip()
                    ]

                    return {
                        "author": author,
                        "story_title": story_title,
                        "ratings": ratings,
                        "blurb": blurb,
                        "category": category,
                        "publication_date": publication_date,
                        "story_links": link,
                    }

    return {}


async def fetch_homepage(urls: list):
    async with hishel.AsyncCacheClient() as client:
        tasks = [fetch_page_data(url, client) for url in urls]
        parsed_pages = await asyncio.gather(*tasks)

    # print(parsed_pages)

    with open("db/parsed_pages.json", "w") as f:
        json.dump(parsed_pages, f, indent=4)


def main():
    start = time.perf_counter()

    url_list = read_urls(URL_LIST)

    try:
        asyncio.run(fetch_homepage(url_list))
    except (ValueError, TypeError, Exception) as e:
        print(f"An error occurred: {e}")

    end = time.perf_counter()
    print(f"Time: {end - start:0.2f} seconds")


if __name__ == "__main__":
    main()
