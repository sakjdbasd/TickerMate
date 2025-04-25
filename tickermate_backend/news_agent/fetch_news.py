import requests
import os
from dotenv import load_dotenv
from .utils import get_time_diff
from datetime import datetime, timedelta, timezone


load_dotenv()
api_key = os.getenv('MARKETAUX_API_KEY')

def fetch_headline_news(ticker, api_key,limit=3,hours=24):
    now = datetime.now(timezone.utc)
    today = now - timedelta(hours=hours)

    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "api_token": api_key,
        "symbols": ticker,
        "language": "en",
        "limit": limit,
        "published_before":now.strftime('%Y-%m-%dT%H:%M:%S'),
        "published_after":today.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    # headers = {"Authorization": f"Bearer {api_key}"}
    res = requests.get(url,params=params)
    # return res.json()
    result = []
    if res.status_code == 200:
        articles = res.json().get("data",[])
    else:
        print(f"Fail to fetch news: {res.status_code}")
        articles = []
    # return articles

    for article in articles:
        published_at = article.get("published_at","")
        result.append({
            "title": article.get("title", ""),
            "description": article.get("description", "") or article.get("snippet", ""),
            "source": article.get("source", ""),
            "published_at": published_at,
            "time_ago": get_time_diff(published_at)
        })

    return result
    
# testing
# if __name__ == "__main__":
#     articles = fetch_headline_news("MSFT",api_key)
#     print(articles)
    # for idx,article in enumerate(articles,1):
    #     print(f"\n News {idx}: {article['title']}\n{article['description']}\n{article['source']['name']}\n{article['publishedAt']}\n")
    # print(fetch_headline_news("MSFT",api_key))