import os
from datetime import datetime, timedelta, timezone

import yaml
from Entries import Entries

# Get the RSS feed URL
config_path = os.path.join(os.path.dirname(__file__), "config.yml")

with open(config_path, "r") as f:
    channel_id = yaml.safe_load(f)["channel_id"]
    entries = Entries(channel_id).get_entries(
        start_date=datetime.now(tz=timezone.utc) - timedelta(days=90)
    )
    print(entries)
