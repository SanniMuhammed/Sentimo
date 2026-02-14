"""RSS news feed collector."""
import os, sys, logging, hashlib
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from storage.db import get_conn, insert_post, insert_sentiment, insert_entity
from analysis.sentiment import analyze
from analysis.entities import extract

logger = logging.getLogger(__name__)


def collect():
    """Collect articles from RSS feeds."""
    try:
        import feedparser
    except ImportError:
        logger.error("feedparser not installed. Run: pip install feedparser")
        return 0

    conn = get_conn()
    count = 0
    for source_name, url in config.RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:30]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")[:2000]
                published = entry.get("published_parsed")
                if published:
                    created = datetime(*published[:6], tzinfo=timezone.utc).isoformat()
                else:
                    created = datetime.now(timezone.utc).isoformat()

                post_id = f"news_{hashlib.md5((link or title).encode()).hexdigest()[:12]}"
                now_iso = datetime.now(timezone.utc).isoformat()
                post_data = {
                    "id": post_id,
                    "source": "news",
                    "subreddit": None,
                    "title": title,
                    "body": summary,
                    "author": source_name,
                    "url": link,
                    "score": 0,
                    "num_comments": 0,
                    "created_at": created,
                    "collected_at": now_iso,
                }
                insert_post(conn, post_data)

                text = f"{title} {summary}"
                sentiment = analyze(text)
                insert_sentiment(conn, post_id, sentiment)
                for entity_name, entity_type in extract(text):
                    insert_entity(conn, post_id, entity_name, entity_type)
                count += 1
        except Exception as e:
            logger.error(f"Error collecting {source_name}: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Collected {count} news articles")
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collect()
