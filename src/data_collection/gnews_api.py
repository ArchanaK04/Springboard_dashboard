import os
import requests
import pandas as pd
from datetime import datetime, timedelta

GNEWS_KEY = os.getenv("GNEWS_KEY")
GNEWS_URL = "https://gnews.io/api/v4/search"

def fetch_gnews(
    keyword: str,
    from_date: str,
    to_date: str = None,
    max_articles: int = 20
):
    """
    Fetch from GNews given a keyword, date range, and article count.
    Dates should be strings in YYYY-MM-DD format.
    """
    assert GNEWS_KEY, "Missing GNEWS_KEY in .env"
    
    if to_date is None:
        to_date = datetime.utcnow().strftime("%Y-%m-%d")  # default to today if not provided

    date_from = pd.to_datetime(from_date).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to = pd.to_datetime(to_date).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_rows = []
    collected = 0
    page = 1
    page_size = min(100, max_articles)
    while collected < max_articles:
        params = {
            "q": keyword,
            "token": GNEWS_KEY,
            "lang": "en",
            "from": date_from,
            "to": date_to,
            "max": page_size,
            "page": page,
        }
        r = requests.get(GNEWS_URL, params=params, timeout=10)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        for a in articles:
            all_rows.append({
                "keyword": keyword,
                "title": a.get("title"),
                "description": a.get("description"),
                "content": a.get("content"),
                "source": a.get("source", {}).get("name"),
                "author": a.get("author"),
                "url": a.get("url"),
                "published_at": a.get("publishedAt"),
            })
        collected += len(articles)
        if len(articles) < page_size:
            break
        page += 1
    df = pd.DataFrame(all_rows)
    if not df.empty:
        df["published_at"] = pd.to_datetime(df["published_at"])
        df["date"] = df["published_at"].dt.date
        df["text"] = df[["title", "description", "content"]].astype(str).agg(" ".join, axis=1)
        df = df.drop_duplicates(subset=["keyword", "title", "url"]).reset_index(drop=True)
    return df
