from fetch_news import fetch_headline_news
from gpt_summary import summarize_financial_news
import os
from dotenv import load_dotenv

load_dotenv()

def get_summarized_news(ticker, news_api_key, openai_api_key):
    raw_news = fetch_headline_news(ticker, news_api_key)
    summaries = []
    for news in raw_news:
        result = summarize_financial_news(news["description"], openai_api_key)
        # print(result)
        summaries.append(            
            {
                "title": news["title"],
                "summary": result.get("summary",""),
                "sentiment": result.get("sentiment","unknown"),
                "source": news["source"]
            })

    return summaries

if __name__ == "__main__":
    summaries = get_summarized_news(
        "MSFT",
        news_api_key=os.getenv("NEWS_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    # print(summaries)
    for item in summaries:
        print(f"\n🔹 {item['title']}\n📝 {item['summary']}\n{item['sentiment']}\n{item['source']}\n")
