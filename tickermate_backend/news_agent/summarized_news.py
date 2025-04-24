from .fetch_news import fetch_headline_news
from .gpt_summary import summarize_financial_news
import os
from dotenv import load_dotenv
from .utils import parse_published_time,clean_gpt_text
import yfinance as yf

load_dotenv()

def get_summarized_news(ticker, news_api_key, openai_api_key):
    etf = yf.Ticker(ticker)
    info = etf.info
    fast_info = etf.fast_info

    last_price = fast_info["lastPrice"]
    previous_close = fast_info["previousClose"]

    change = (last_price - previous_close) / previous_close * 100
    raw_news = fetch_headline_news(ticker, news_api_key)
    # raw_news.sort(key=lambda x: parse_published_time(x["published_at"]), reverse=False)
    summaries = {"ticker": ticker,
                 "name": info.get("shortName"),
                 "sector": info.get("sector"),
                 "price": str(round(last_price,2)),
                 "change": str(round(change,2)) + "%",
                 "AI Hightlight":"",
                 "News Summary":[],
    }
    for idx,news in enumerate(raw_news):
        word_limit = 50 if idx == 0 else 15
        result = summarize_financial_news(news["description"], openai_api_key, word_limit)
        # summary_text = result.get("summary", "").strip().strip('"').strip("'").strip(",")
        # sentiment_text = result.get("sentiment", "").strip('"').strip("'").strip(",")
        summary_text = clean_gpt_text(result.get("summary", ""))
        sentiment_text = clean_gpt_text(result.get("sentiment", ""))
        # print(result)
        if idx == 0:
            summaries["AI Hightlight"] = summary_text
        else: 
            summaries["News Summary"].append(            
                {
                    "time": news["time_ago"],
                    # "title": news["title"],
                    "source": news["source"],
                    "sentiment": sentiment_text,
                    "summary": summary_text,
                    # "published_at": news["published_at"],
                })

    return summaries

# if __name__ == "__main__":
#     summaries = get_summarized_news(
#         "AMZN",
#         news_api_key=os.getenv("NEWS_API_KEY"),
#         openai_api_key=os.getenv("OPENAI_API_KEY"),
#     )
#     print(summaries)
    # for item in summaries:
    #     print(f"\n🔹 {item['title']}\n📝 {item['summary']}\n{item['sentiment']}\n{item['source']}\n{item['time_ago']}\n")
