from fetch_news import fetch_headline_news
from gpt_summary import summarize_financial_news

def get_summarized_news(news_api_key, openai_api_key):
    raw_news = fetch_headline_news(news_api_key)
    summaries = [
        {
            "title": news["title"],
            "summary": summarize_financial_news(news["description"] or news["content"] or "", openai_api_key)
        }
        for news in raw_news
    ]
    return summaries
