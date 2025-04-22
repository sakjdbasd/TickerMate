from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def summarize_financial_news(text,api_key):
    # client = OpenAI(api_key=os.environ.get(api_key))
    client = OpenAI(api_key=api_key)
    prompt = f"""
        The following is an economic news article. 
        Please summarize the essence of the article in plain language and briefly analyze its possible impact on the market
        (within 50 words):
        """ + text
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7
        )

    # return response
    return response.choices[0].message.content.strip()

# testing
if __name__ == "__main__":
    text = "UnitedHealth Group stock had one of its worst days ever on Thursday after the healthcare giant unexpectedly cut its profit forecast for the year."
    summary = summarize_financial_news(text,api_key)
    print(summary)