from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def summarize_financial_news(text,api_key,word_limit):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    The following is a financial news article:

    ----
    {text}
    ----

    Task:
    1. Summarize the key message in plain English (within {word_limit} words).
    2. Classify the **market sentiment** as one of: Bullish / Bearish / Neutral.
    Return your answer in the following JSON format:
    {{
        "summary": "...",
        "sentiment": "..."
    }}
    """
    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7
        )

    # return response
    content = response.choices[0].message.content.strip()
    # return content
    # result = json.loads(content)
    # return result

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        # print("JSON decode failed:", e)
        lines = content.splitlines()
        summary = ""
        sentiment = "Unknown"
        for line in lines:
            if "summary" in line.lower():
                summary = line.split(":", 1)[-1].strip()
            if "sentiment" in line.lower():
                sentiment = line.split(":", 1)[-1].strip()
        return {
            "summary": summary or "Summary unavailable.",
            "sentiment": sentiment or "Unknown"
        }

# testing
# if __name__ == "__main__":
#     text = "UnitedHealth Group stock had one of its worst days ever on Thursday after the healthcare giant unexpectedly cut its profit forecast for the year."
#     summary = summarize_financial_news(text,api_key,20)
#     print(summary)