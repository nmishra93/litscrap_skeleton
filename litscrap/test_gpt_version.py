import asyncio
from dataclasses import dataclass
import time
import datetime
from urllib.parse import urljoin
import json
import hishel
import httpx
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
    stroy_link: str


@dataclass
class Response:
    body_html: HTMLParser


def read_urls(file: str):
    with open(file, "r", encoding="utf-8") as f:
        return f.read().splitlines()


# Function to extract data from authsoup
def clean_text(text):
    return text.replace("(", "").replace(")", "")


# Function to extract ratings from authors
def extract_ratings(authors):
    return [float(author.split("\xa0")[1]) for author in authors]


async def fetch_homepage(urls):
    async with hishel.AsyncCacheClient() as client:
        response = [client.get(url, headers=HEADERS) for url in urls]
        results = await asyncio.gather(*response)

        parsed_pages = []

        for result in results:
            html = HTMLParser(result.text)

            # Fix: Check if ".contactheader" exists before accessing text
            author_element = html.css_first(".contactheader", default="not found")
            author = author_element.text() if author_element else None

            # Check if ".fc" elements exist before processing
            stories = html.css(".fc")
            if stories:
                stories = [story.text() for story in stories]
                story_title = [item.split("\xa0")[0] for item in stories]
                authors = [clean_text(item) for item in stories]
                ratings = extract_ratings(authors)
                # get story links
                story_links = html.css(".fc a")
                link = [link.attributes["href"] for link in story_links]

                # Check if "div td:nth-child(2)" elements exist before processing
                blurbs = html.css("div td:nth-child(2)")
                if blurbs:
                    blurb = [
                        blurb.text().split("\xa0")[0].strip()
                        for blurb in blurbs
                        if blurb.text().strip()
                    ]

                    # Check if ".r-5 span" elements exist before processing
                    categories = html.css(".r-5 span")
                    if categories:
                        category = [category.text().strip() for category in categories]

                        # Check if "div td:nth-child(4)" elements exist before processing
                        dates = html.css("div td:nth-child(4)")
                        if dates:
                            publication_date = [
                                date.text().strip()
                                for date in dates
                                if date.text().strip()
                            ]

                            parsed_pages.append(
                                {
                                    "author": author,
                                    "story_title": story_title,
                                    "ratings": ratings,
                                    "blurb": blurb,
                                    "category": category,
                                    "publication_date": publication_date,
                                    "story_links": link,
                                }
                            )

        # print(parsed_pages)

        # export to json
        with open("parsed_pages.json", "w") as f:
            json.dump(parsed_pages, f, indent=4)


def main():
    start = time.perf_counter()

    url_list = read_urls(URL_LIST)

    try:
        asyncio.run(fetch_homepage(url_list))
    except ValueError as e:
        print(f"A ValueError occurred: {e}")
    except TypeError as e:
        print(f"A TypeError occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    end = time.perf_counter()

    print(f"Time: {end - start:0.2f} seconds")
