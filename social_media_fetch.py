import os
import re
import tweepy
import praw
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from colorama import Fore, Style  # For colored output
import json


class SocialMediaHarvester:
    def __init__(self, config: Dict):
        self.config = config
        
        # Only initialize what's needed
        if not config.get("STOCKTWITS_ONLY"):
            
            pass

    def fetch_twitter_data(self, symbol: str, hours_old: int = 24):
        if not self.config.get("TWITTER_BEARER_TOKEN"):
            print("Twitter API not configured")
            return []
        # Rest of original code

    def fetch_reddit_data(self, symbol: str, limit: int = 50):
        if not self.config.get("REDDIT_CLIENT_ID"):
            print("Reddit API not configured")
            return []

    def fetch_stocktwits_data(self, symbol: str):
        # Works without authentication
        try:
            response = requests.get(
                f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json",
                params={"limit": 100}
            )
            return [{
                "text": self._clean_text(msg['body']),
                "source": "stocktwits",
                "likes": msg['likes']['total'],
                "time": datetime.strptime(msg['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            } for msg in response.json()['messages']]
        except Exception as e:
            print(f"StockTwits Error: {e}")
            return []

def print_payload(payload: dict, max_samples=3):
    """Pretty-print the social media payload with sample data"""
    print(f"\n{Fore.YELLOW}=== SOCIAL MEDIA DATA FOR {payload['symbol']} ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}Time Range:{Style.RESET_ALL} {payload['time_range']}")
    print(f"{Fore.CYAN}Total Posts:{Style.RESET_ALL} {payload['total_posts']}\n")

    for platform, data in payload['platform_data'].items():
        print(f"{Fore.GREEN}▶ {platform.upper()} ({len(data)} posts){Style.RESET_ALL}")
        
        if not data:
            print(f"{Fore.RED}  No data found{Style.RESET_ALL}")
            continue
            
        for i, post in enumerate(data[:max_samples]):
            print(f"  {Fore.WHITE}Sample {i+1}:{Style.RESET_ALL}")
            print(f"  {Fore.MAGENTA}Text:{Style.RESET_ALL} {post['text'][:100]}...")
            print(f"  {Fore.BLUE}Engagement:{Style.RESET_ALL} {post.get('likes', post.get('upvotes', 0))}")
            print(f"  {Fore.BLUE}Time:{Style.RESET_ALL} {post['time'].strftime('%Y-%m-%d %H:%M UTC')}")
        
        if len(data) > max_samples:
            print(f"  {Fore.WHITE}... and {len(data)-max_samples} more posts{Style.RESET_ALL}")
        print("-" * 50)

    # Print JSON structure summary
    print(f"\n{Fore.YELLOW}=== PAYLOAD STRUCTURE ==={Style.RESET_ALL}")
    print(json.dumps({k: type(v).__name__ for k, v in payload.items()}, indent=2))
    print(f"\n{Fore.YELLOW}=== SAMPLE FOR LLM INPUT ==={Style.RESET_ALL}")
    print(generate_llm_prompt(payload)[:500] + "...")

# Add this to your existing class
def generate_llm_prompt(payload: Dict) -> str:
    return f"""Analyze social sentiment for {payload['symbol']} stock using this data:
    
    {json.dumps(payload['platform_data'], indent=2)}
    
    Consider post engagement and timeliness. Return JSON format:
    {{
        "sentiment_score": -1 to 1,
        "key_bullish": [3 main reasons],
        "key_bearish": [3 main concerns],
        "confidence": 0-100%
    }}"""

# Example Usage
if __name__ == "__main__":
    # Proper config setup (save this in a separate config.py file)
    config = {
        "TWITTER_BEARER_TOKEN": "YOUR_TWITTER_BEARER_TOKEN",
        "TWITTER_API_KEY": "YOUR_TWITTER_API_KEY",
        "TWITTER_API_SECRET": "YOUR_TWITTER_API_SECRET",
        "REDDIT_CLIENT_ID": "YOUR_REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET": "YOUR_REDDIT_CLIENT_SECRET"
    }

# If you don't have Twitter/Reddit API keys yet, use this minimal version:
    config = {
        "STOCKTWITS_ONLY": True  # Doesn't require authentication
    }
    
    harvester = SocialMediaHarvester(config)
    payload = harvester.prepare_llm_payload("AAPL")
    print_payload(payload)
    # Example payload structure:
    # {
    #   "symbol": "AAPL",
    #   "total_posts": 342,
    #   "time_range": "Last 24 hours...",
    #   "platform_data": {
    #       "twitter": [...],
    #       "reddit": [...],
    #       "stocktwits": [...]
    #   }
    # }