import feedparser

RSS_URL = "https://status.openai.com/history.rss"

def main():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("No status updates found.")
        return

    latest_entry = feed.entries[0]

    title = latest_entry.get("title", "Unknown Product")
    summary = latest_entry.get("summary", "No details available")

    print("Latest OpenAI Status Update")
    print("---------------------------")
    print(f"Product: {title}")
    print(f"Status: {summary}")


if __name__ == "__main__":
    main()