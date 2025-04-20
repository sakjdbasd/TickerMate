import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('NEWS_API_KEY')

def fetch_headline_news(api_key):
    url = "https://newsapi.org/v2/top-headlines?category=business&language=en"
    headers = {"Authorization": f"Bearer {api_key}"}
    res = requests.get(url,headers=headers)
    # return res.json()
    return res.json().get("articles",[])[:5]
    

# testing
if __name__ == "__main__":
    articles = fetch_headline_news(api_key)
    print(articles)
    # for idx,article in enumerate(articles,1):
    #     # print(f"\n News {idx}:{article["title"]}\n{article["description"]}\n")
    #     print(f"\n News {idx}: {article['title']}\n{article['description']}\n")