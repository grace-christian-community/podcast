import os
from datetime import datetime
from typing import List

import requests
import yaml
import yt_dlp
from bs4 import BeautifulSoup
from dateutil.parser import parse as rfc2822_parse
from tqdm import tqdm


class Entries:
    class Entry:
        def __init__(
            self,
            title: str,
            link: str,
            id: str,
            description: str,
            datetime: datetime,
        ):
            self.title = title
            self.link = link
            self.id = id
            self.description = description
            self.datetime = datetime
            self.duration = 0
            self.size = 0

        def __repr__(self) -> str:
            return f"Entry({self.id}, ...)"

    def __init__(self, channel_id: str) -> None:
        self.entries: List[self.Entry] = []

        rss_feed_url = (
            f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        )

        # Parse the RSS feed
        response = requests.get(rss_feed_url)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all("entry")

        # Extract data from each <entry> tag and create Entry objects
        for item in items:
            entry = self.Entry(
                title=item.find("title").text,
                link=item.find("link").get("href"),
                id=item.find("yt:videoId").text,
                description=item.find("media:description").text,
                datetime=rfc2822_parse(item.find("published").text),
            )

            self.entries.append(entry)


# Initialize paths
config_path = os.path.join(os.path.dirname(__file__), "_config.yml")
episodes_path = os.path.join(os.path.dirname(__file__), "_data/episodes.yml")

# Get the RSS feed URL
with open(config_path, "r") as f:
    channel_id = yaml.safe_load(f)["channel_id"]
    entries = Entries(channel_id).entries

# Get currently saved episode IDs
with open(episodes_path, "r") as episodes_file:
    existing_ids = []
    episodes = yaml.safe_load(episodes_file)

    if episodes is not None:
        for episode in episodes:
            if "id" in episode:
                existing_ids.append(episode["id"])

print()

# Update episodes YAML
for entry in tqdm(entries):
    # Skip this iteration if the ID is already in the YAML file
    if entry.id in existing_ids:
        continue

    # Download audio
    ydl_opts = {
        "format": "mp3/bestaudio/best",
        "outtmpl": f"assets/audio/{entry.id}.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
        "prefer_ffmpeg": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([entry.link])
            video_info = ydl.extract_info(entry.link, download=False)
            entry.duration = video_info.get("duration")
            entry.size = os.path.getsize(f"assets/audio/{entry.id}.mp3")
    except yt_dlp.utils.DownloadError:
        continue

    # Add to episodes list
    with open(episodes_path, "a") as episodes_file:
        title = (
            entry.title.replace('"', '\\"')
            .replace("\n", "<br />")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        description = (
            entry.description.replace('"', '\\"')
            .replace("\n", "<br />")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        episodes_file.write(
            f"""\
- title: \"{title}\"
  description: \"{description}\"
  id: \"{entry.id}\"
  date: \"{entry.datetime}\"
  duration: \"{entry.duration}\"
  size: \"{entry.size}\"
"""
        )
