from .summarized_news import get_summarized_news
import os
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import JsonResponse

load_dotenv()

def summarized_news_api(request):
    ticker = request.GET.get("ticker", "").upper()
    if not ticker:
        return JsonResponse({"error": "Missing ticker symbol"}, status=400)

    news_api_key = os.getenv("NEWS_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    try:
        data = get_summarized_news(ticker, news_api_key, openai_api_key)
        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


