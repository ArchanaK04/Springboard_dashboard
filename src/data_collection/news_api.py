import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/everything"


def fetch_newsapi(
    keyword: str,
    from_date: str,
    to_date: str = None,
    max_articles: int = 20,
):
    """
    Fetch news given a keyword, date range, and article limit.
    from_date and to_date are strings in YYYY-MM-DD format.
    to_date is optional; defaults to current date if not provided.
    Returns a pandas DataFrame.
    """
    assert NEWSAPI_KEY, "Missing NEWSAPI_KEY in .env"

    if to_date is None:
        to_date = datetime.utcnow().strftime("%Y-%m-%d")

    all_rows = []
    page = 1
    page_size = 100  # NewsAPI max page size
    articles_collected = 0

    while articles_collected < max_articles:
        params = {
            "q": keyword,
            "from": from_date,
            "to": to_date,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(page_size, max_articles - articles_collected),
            "page": page,
            "apiKey": NEWSAPI_KEY,
        }
        r = requests.get(NEWSAPI_URL, params=params, timeout=10)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        if not articles:
            break  # No more articles

        for article in articles:
            all_rows.append({
                "keyword": keyword,
                "title": article.get("title"),
                "description": article.get("description"),
                "content": article.get("content"),
                "source": article.get("source", {}).get("name"),
                "author": article.get("author"),
                "url": article.get("url"),
                "published_at": article.get("publishedAt"),
            })

        articles_collected += len(articles)
        if len(articles) < params["pageSize"]:
            break  # Reached end
        page += 1

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df["published_at"] = pd.to_datetime(df["published_at"])
        df["date"] = df["published_at"].dt.date
        df["text"] = df[["title", "description", "content"]].astype(str).agg(" ".join, axis=1)
        df = df.drop_duplicates(subset=["keyword", "title", "url"]).reset_index(drop=True)

    return df
