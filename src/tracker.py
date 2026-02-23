import time
import feedparser
import os

RSS_URL = "https://status.openai.com/history.rss"
CHECK_INTERVAL_SECONDS = 300  # 5 minutes
STATE_FILE = ".state"

def load_last_seen_id():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return f.read().strip() or None


def save_last_seen_id(entry_id):
    with open(STATE_FILE, "w") as f:
        f.write(entry_id)


def fetch_updates(last_seen_id=None):
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return last_seen_id

    for entry in reversed(feed.entries):
        entry_id = entry.get("id", entry.get("link"))

        if entry_id == last_seen_id:
            continue

        title = entry.get("title", "Unknown Product")
        summary = entry.get("summary", "No details available")

        print("New OpenAI Status Update")
        print("------------------------")
        print(f"Product: {title}")
        print(f"Status: {summary}")
        print()

        last_seen_id = entry_id
        save_last_seen_id(entry_id)

    return last_seen_id


def main():
    last_seen_id = None
    print("OpenAI Status Tracker started\n")
    last_seen_id = load_last_seen_id()

    while True:
        last_seen_id = fetch_updates(last_seen_id)
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()