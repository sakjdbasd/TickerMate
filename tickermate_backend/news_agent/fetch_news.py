import requests
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta, timezone
from .fetch_news_marketaux import fetch_headline_news_marketaux
from .fetch_news_news_api import fetch_headline_news_news_api


load_dotenv()
news_api_key = os.getenv('NEWS_API_KEY')
marketaux_api_key = os.getenv('MARKETAUX_API_KEY')

def fetch_headline_news(ticker, news_api_key, marketaux_api_key, mode):
    if mode == "day":
        return fetch_headline_news_news_api(ticker,news_api_key)
    elif mode == "hour":
        return fetch_headline_news_marketaux(ticker,marketaux_api_key)
    else:
        raise ValueError("Invalid mode. Please use 'day' or 'hour'.")


# testing
# if __name__ == "__main__":
#     articles = fetch_headline_news("MSFT",news_api_key,marketaux_api_key,"day")
#     print(articles)