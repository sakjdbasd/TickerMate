import requests

def fetch_headline_news(api_key):
    url = ""
    headers = {}
    res = requests.get(url,headers=headers)
    return res.json().get("articles",[])[:5]