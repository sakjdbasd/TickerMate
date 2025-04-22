from fetch_news import fetch_headline_news
from gpt_summary import summarize_financial_news
import os
from dotenv import load_dotenv
from utils import parse_published_time

load_dotenv()

def get_summarized_news(ticker, news_api_key, openai_api_key):
    raw_news = fetch_headline_news(ticker, news_api_key)
    # raw_news.sort(key=lambda x: parse_published_time(x["published_at"]), reverse=False)
    summaries = []
    for idx,news in enumerate(raw_news):
        word_limit = 50 if idx == 0 else 15
        result = summarize_financial_news(news["description"], openai_api_key,word_limit)
        # print(result)
        summaries.append(            
            {
                "title": news["title"],
                "summary": result.get("summary",""),
                "sentiment": result.get("sentiment","unknown"),
                "source": news["source"],
                "published_at": news["published_at"],
                "time_ago": news["time_ago"],
            })

    return summaries

if __name__ == "__main__":
    summaries = get_summarized_news(
        "AMZN",
        news_api_key=os.getenv("NEWS_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    # print(summaries)
    for item in summaries:
        print(f"\n🔹 {item['title']}\n📝 {item['summary']}\n{item['sentiment']}\n{item['source']}\n{item['time_ago']}\n")
