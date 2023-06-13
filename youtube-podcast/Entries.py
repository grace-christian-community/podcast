from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as rfc2822_parse


class Entries:
    class Entry:
        def __init__(
            self, title: str, link: str, id: str, description: str, time: datetime
        ):
            self.title = title
            self.link = link
            self.id = id
            self.description = description
            self.time = time

        def __repr__(self) -> str:
            return f"Entry({self.id}, ...)"

    def __init__(self, channel_id: str) -> None:
        self._entries: List[self.Entry] = []

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
                description=item.find("description").text,
                time=rfc2822_parse(item.find("published").text),
            )

            self._entries.append(entry)

    def get_entries(self, start_date: datetime) -> List[Entry]:
        return [entry for entry in self._entries if entry.time >= start_date]
