"""Reddit data collector using PRAW."""
import os, sys, logging
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from storage.db import get_conn, insert_post
from analysis.sentiment import analyze
from analysis.entities import extract
from storage.db import insert_sentiment, insert_entity

logger = logging.getLogger(__name__)


def collect():
    """Collect posts from configured subreddits."""
    if not config.REDDIT_CLIENT_ID:
        logger.warning("Reddit API credentials not set. Skipping Reddit collection.")
        return 0

    try:
        import praw
    except ImportError:
        logger.error("praw not installed. Run: pip install praw")
        return 0

    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )

    conn = get_conn()
    count = 0
    for sub_name in config.SUBREDDITS:
        try:
            subreddit = reddit.subreddit(sub_name)
            for post in subreddit.hot(limit=config.REDDIT_POST_LIMIT):
                post_id = f"reddit_{post.id}"
                now_iso = datetime.now(timezone.utc).isoformat()
                created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat()
                post_data = {
                    "id": post_id,
                    "source": "reddit",
                    "subreddit": sub_name,
                    "title": post.title,
                    "body": (post.selftext or "")[:2000],
                    "author": str(post.author) if post.author else "[deleted]",
                    "url": f"https://reddit.com{post.permalink}",
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_at": created,
                    "collected_at": now_iso,
                }
                insert_post(conn, post_data)

                # Analyze
                text = f"{post.title} {post.selftext or ''}"
                sentiment = analyze(text)
                insert_sentiment(conn, post_id, sentiment)
                for entity_name, entity_type in extract(text):
                    insert_entity(conn, post_id, entity_name, entity_type)
                count += 1
        except Exception as e:
            logger.error(f"Error collecting r/{sub_name}: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Collected {count} Reddit posts")
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collect()
