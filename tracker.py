import json
import os
import requests
from yt_dlp import YoutubeDL

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEEN_FILE = "seen_videos.json"
CHANNEL_FILE = "channels.txt"


# --------------------------
# Load Seen Videos
# --------------------------

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        seen_videos = set(json.load(f))
else:
    seen_videos = set()


# --------------------------
# Load Channels
# --------------------------

with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
    CHANNELS = [
        line.strip()
        for line in f.readlines()
        if line.strip()
    ]


# --------------------------
# Telegram
# --------------------------

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


# --------------------------
# Save Database
# --------------------------

def save_seen():

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            list(seen_videos),
            f,
            ensure_ascii=False,
            indent=2
        )


# --------------------------
# Fetch Shorts
# --------------------------

def get_channel_shorts(handle):

    url = f"https://www.youtube.com/{handle}/shorts"

    opts = {
        "quiet": True,
        "extract_flat": True,
        "playlistend": 10
    }

    try:

        with YoutubeDL(opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            return info.get("entries", [])

    except Exception as e:

        print(f"Error {handle}")
        print(e)

        return []


# --------------------------
# Full Video Details
# --------------------------

def get_video_info(video_id):

    url = f"https://www.youtube.com/watch?v={video_id}"

    opts = {
        "quiet": True
    }

    try:

        with YoutubeDL(opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            return info

    except Exception as e:

        print("Video Error:", e)

        return None


# --------------------------
# Main
# --------------------------
FIRST_RUN = len(seen_videos) == 0
new_found = 0

for handle in CHANNELS:

    print("Checking:", handle)

    shorts = get_channel_shorts(handle)

    if not shorts:
        continue

    for short in reversed(shorts):

        video_id = short.get("id")

        if not video_id:
            continue

        if video_id in seen_videos:
            continue

        details = get_video_info(video_id)

        if not details:
            continue

        channel_name = details.get(
            "channel",
            "Unknown"
        )

        title = details.get(
            "title",
            "No title"
        )

        description = details.get(
            "description",
            ""
        )

        video_url = (
            f"https://youtube.com/watch?v={video_id}"
        )

        message = f"""
🔥 NEW SHORT

📺 Channel:
{channel_name}

🎬 Title:
{title}

📝 Description:
{description[:1500]}

🔗 Link:
{video_url}
"""

        if not FIRST_RUN:
    	    send_telegram(message)

        seen_videos.add(video_id)

        new_found += 1

save_seen()

print(
    f"Finished. New videos found: {new_found}"
)
