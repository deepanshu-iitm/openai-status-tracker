import time
import feedparser
import os
from datetime import datetime
import html
import re

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

def clean_html(raw_html: str) -> list[str]:
    if not raw_html:
        return []

    text = html.unescape(raw_html)

    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines

    return "\n".join(lines)

def fetch_updates(last_seen_id=None):
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        return last_seen_id

    for entry in reversed(feed.entries):
        entry_id = entry.get("id", entry.get("link"))

        if entry_id == last_seen_id:
            continue

        title = entry.get("title", "Unknown Product")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        lines = clean_html(entry.get("summary", ""))

        status = "Unknown"
        description = []
        components = []

        for line in lines:
            lower = line.lower()

            if lower.startswith("status:"):
                status = line.split(":", 1)[1].strip()

            elif lower == "affected components":    
                continue

            elif line.startswith("-"):
                components.append(line)

            else:
                description.append(line)

        print(f"[{timestamp}]")
        print(f"Product: {title}")
        print(f"Status: {status}")

        for line in description:
            print(line)

        if components:
            print("Affected components:")
            for c in components:
                print(c)

        print("-" * 60)

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