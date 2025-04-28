from .summarized_news import get_summarized_news
import os
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

load_dotenv()

@api_view(["GET"])
def summarized_news_api(request):
    ticker = request.GET.get("ticker", "").upper()
    mode = request.GET.get("mode","").lower()
    if not ticker:
        # return JsonResponse({"error": "Missing ticker symbol"}, status=400)
        return Response({"error": "Missing ticker symbol"}, status=status.HTTP_400_BAD_REQUEST)

    news_api_key = os.getenv("NEWS_API_KEY")
    marketaux_api_key = os.getenv("MARKETAUX_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    try:
        data = get_summarized_news(ticker, news_api_key, marketaux_api_key, openai_api_key, mode)
        # return JsonResponse(data, safe=False, status=200)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        # return JsonResponse({"error": str(e)}, status=500)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


