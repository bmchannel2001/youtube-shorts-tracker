import json
import os
import requests
import feedparser

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEEN_FILE = "seen_videos.json"
CHANNEL_FILE = "channels.txt"

# Load seen videos
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        seen_videos = set(json.load(f))
else:
    seen_videos = set()

# Load channel IDs
with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
    CHANNELS = [
        line.strip()
        for line in f.readlines()
        if line.strip()
    ]


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg[:4000],
            "disable_web_page_preview": False
        },
        timeout=30
    )


def save_seen():
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            list(seen_videos),
            f,
            ensure_ascii=False,
            indent=2
        )


FIRST_RUN = len(seen_videos) == 0

new_found = 0

for channel_id in CHANNELS:

    rss_url = (
        f"https://www.youtube.com/feeds/videos.xml"
        f"?channel_id={channel_id}"
    )

    feed = feedparser.parse(rss_url)

    for entry in reversed(feed.entries[:10]):

        video_id = entry.yt_videoid

        if video_id in seen_videos:
            continue

        title = entry.title
        channel_name = entry.author

        video_url = (
            f"https://www.youtube.com/watch?v={video_id}"
        )

        message = f"""🔥 NEW SHORT/VIDEO

📺 Channel: {channel_name}

🎬 Title:
{title}

🔗 Link:
{video_url}
"""

        if not FIRST_RUN:
            send_telegram(message)

        seen_videos.add(video_id)

        new_found += 1

save_seen()

print(f"Finished. New videos found: {new_found}")
