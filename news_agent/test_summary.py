# test_summary.py
import os
from dotenv import load_dotenv
from utils import get_summarized_news

load_dotenv()

if __name__ == "__main__":
    summaries = get_summarized_news(
        news_api_key=os.getenv("NEWS_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    # print(summaries)
    for item in summaries:
        print(f"\n🔹 {item['title']}\n📝 {item['summary']}\n")
    
