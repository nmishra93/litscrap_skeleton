import os
import shutil
import json

os.getcwd()

with open("./db/parsed_pages.json", "r") as f:
    data = json.load(f)

for author in data:
    author_name = author["author"]
    story_list = author["story_links"]

    # Create author directory
    author_directory = os.path.join(os.getcwd(), "export", author_name)
    if not os.path.exists(author_directory):
        os.makedirs(author_directory)
    # print(author_name)

    for index, link in enumerate(story_list):
        story_filename = link.split("/")[-1].title().replace("-", " ")
        story_path = os.path.join(author_directory, story_filename)

        print(story_path)
        # print(link)

        # # Use requests to download the content [PLACEHOLDER]
        # will change it to use asyncio and httpx
        # response = requests.get(link)
        # if response.status_code == 200:
        #     with open(story_path, "wb") as story_file:
        #         story_file.write(response.content)
        # else:
        #     print(f"Failed to download {link}. Status code: {response.status_code}")

        # For simplicity, let's assume you're copying an existing file for each link
        # need to work on this as well.
        shutil.copy("existing_story_file.html", story_path)
