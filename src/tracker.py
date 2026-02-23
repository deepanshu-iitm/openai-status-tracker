import time
import feedparser
import os
from datetime import datetime
import html
import re

FEEDS = [
    {
        "name": "OpenAI",
        "url": "https://status.openai.com/history.rss",
    },
    # we can add more providers here:
    # {
    #     "name": "Stripe",
    #     "url": "https://status.stripe.com",
    # },
]
CHECK_INTERVAL_SECONDS = 300  # 5 minutes
STATE_DIR = ".state"

def state_file_for(feed_name: str) -> str:
    os.makedirs(STATE_DIR, exist_ok=True)
    return os.path.join(STATE_DIR, f"{feed_name}.state")

def load_last_seen_id(state_file: str):
    if not os.path.exists(state_file):
        return None
    with open(state_file, "r") as f:
        return f.read().strip() or None

def save_last_seen_id(state_file: str, entry_id: str):
    with open(state_file, "w") as f:
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

def fetch_updates(
    feed_url: str,
    provider: str,
    last_seen_id: str | None,
    state_file: str,
):
    feed = feedparser.parse(feed_url)

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
        print(f"Provider: {provider}")
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
        save_last_seen_id(state_file, entry_id)

    return last_seen_id


def main():
    print("Status Tracker started\n")

    last_seen = {}

    for feed in FEEDS:
        state_file = state_file_for(feed["name"])
        last_seen[feed["name"]] = load_last_seen_id(state_file)

    while True:
        for feed in FEEDS:
            name = feed["name"]
            url = feed["url"]
            state_file = state_file_for(name)

            last_seen[name] = fetch_updates(
                feed_url=url,
                provider=name,
                last_seen_id=last_seen[name],
                state_file=state_file,
            )

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()