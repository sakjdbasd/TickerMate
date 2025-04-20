from utils import get_summarized_news
import os
from dotenv import load_dotenv
from django.shortcuts import render

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
news_api_key = os.getenv("NEWS_API_KEY")


def news_summary_view(request):
    summaries = get_summarized_news(
        news_api_key=os.getenv("NEWS_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    return render(request, "news_agent/dashboard.html", {"summaries": summaries})

