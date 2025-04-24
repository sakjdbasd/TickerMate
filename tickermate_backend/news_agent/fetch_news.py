import requests
import os
from dotenv import load_dotenv
from .utils import get_time_diff
from datetime import datetime,timedelta, timezone


load_dotenv()
api_key = os.getenv('NEWS_API_KEY')

def fetch_headline_news(ticker, api_key,limit=4):
    now = datetime.now(timezone.utc)
    today = now - timedelta(hours=18)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": ticker,
        "language": "en",
        "from": today.isoformat()+"Z",
        "to": now.isoformat()+"Z",
        "sortBy": "publishedAt",
        "pageSize": limit
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    res = requests.get(url,headers=headers,params=params)
    # return res.json()
    result = []
    if res.status_code == 200:
        articles = res.json().get("articles",[])
    else:
        print(f"Fail to fetch news: {res.status_code}")
        articles = []
    # return articles

    for article in articles:
        publishedAt = article.get("publishedAt","")
        result.append({
            "title": article.get("title", ""),
            "description": article.get("description", "") or article.get("content", ""),
            "source": article.get("source", {}).get("name", ""),
            "published_at": publishedAt,
            "time_ago": get_time_diff(publishedAt)
        })

    return result
    
# testing
# if __name__ == "__main__":
#     articles = fetch_headline_news("MSFT",api_key)
#     print(articles)
    # for idx,article in enumerate(articles,1):
    #     print(f"\n News {idx}: {article['title']}\n{article['description']}\n{article['source']['name']}\n{article['publishedAt']}\n")
    # print(fetch_headline_news("MSFT",api_key))