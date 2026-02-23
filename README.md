# OpenAI Status Tracker

A lightweight, event-driven Python service that automatically tracks and logs service incidents, outages, and degradation updates from the OpenAI Status Page.

The system consumes the official OpenAI Status RSS feed and prints clean, structured updates to the console whenever a new incident or status update occurs.

---

## Problem Overview

This project was built to automatically detect and log updates related to OpenAI API products (e.g. Chat Completions, Responses, Images, etc.) without relying on manual page refreshes, HTML scraping, or inefficient polling.

The solution is designed to scale efficiently and can be extended to monitor 100+ similar status pages from different providers.

---

## Architecture & Design Decisions

### Event-Driven Data Source

The OpenAI Status Page is powered by Atlassian Statuspage, which provides an official RSS feed:

https://status.openai.com/history.rss

RSS entries are emitted only when incidents or updates occur, making it a natural event-driven source. This avoids scraping, browser automation, or high-frequency polling.

### Change Detection & Idempotency

Each RSS entry has a stable identifier (`id` or `link`).  
The tracker records the last processed entry per provider and ensures that:

- Each incident is logged **exactly once**
- Previously processed updates are never replayed
- Restarts do not cause duplicate output

### Efficient Scheduling

The tracker runs on a low-frequency schedule (default: every 5 minutes).  
Since the RSS feed only changes when incidents occur, this approach is efficient and scalable even when monitoring many providers.

### Scalability

The system is designed to support multiple providers by configuration:

- Each provider has its own RSS feed
- Each provider maintains independent state
- Adding a new provider requires only adding one entry to a list

No architectural changes are required to scale to 100+ status pages.

---

## Project Structure

```
openai-status-tracker/
├── src/
│   └── tracker.py
├── .gitignore
├── README.md
├── requirements.txt
```

---

## Setup Instructions

### 1. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the tracker

From the project root:

```bash
python src/tracker.py
```

The tracker will start immediately and print any new OpenAI service updates to the console.

---

## Example Output

```
[2026-02-23 10:20:49]
Provider: OpenAI
Product: High errors with image generation
Status: Resolved
All impacted services have now fully recovered.
Affected components:
- Images (Operational)
- Image Generation (Operational)
------------------------------------------------------------
```

---

## Extending to Other Providers

To monitor additional status pages, add entries to the `FEEDS` list in `tracker.py`:

```python
FEEDS = [
    {
        "name": "OpenAI",
        "url": "https://status.openai.com/history.rss",
    },
    {
        "name": "AnotherProvider",
        "url": "https://status.example.com/history.rss",
    },
]
```

Each provider is handled independently and maintains its own state.

---


