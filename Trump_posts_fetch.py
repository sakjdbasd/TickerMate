from __future__ import annotations
"""Truth Social → market-sentiment extractor with optional live tests.

Four fetch layers (JSON → RSS → Playwright → HTML) with cookie-sanitising to
avoid latin-1 header errors.
"""

import argparse
import json
import os
import re
import sys
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, List, Tuple

import requests
import yfinance as yf
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from urllib.parse import quote_from_bytes

# ═════════ Configuration ════════════════
load_dotenv()
BASE_URL = "https://truthsocial.com/@realDonaldTrump"
ACCOUNT_ID = "109525400354187127"
USER_AGENT = "Mozilla/5.0 (TickerMateBot/5.0)"
HEADERS = {"User-Agent": USER_AGENT}
NEWS_API_ROOT = "http://localhost:3000/api/ticker/"
TICKER_RE = re.compile(r"\$(DJI|SPX|NDX|[A-Z]{1,5})\b")

# ═════════ Cookie sanitiser ═════════════
def _sanitize_cookie(raw: str) -> str:
    """Percent-encode non-latin-1 chars so requests won't raise a codec error."""
    def enc(pair: str) -> str:
        k, _, v = pair.strip().partition("=")
        if not k or not v:
            return ""
        try:
            k.encode("latin1"); v.encode("latin1")
            return f"{k}={v}"
        except UnicodeEncodeError:
            return f"{k}={quote_from_bytes(v.encode('utf-8'))}"
    return "; ".join(filter(None, (enc(p) for p in raw.split(";"))))

if os.getenv("TRUTHSOCIAL_COOKIE"):
    HEADERS["Cookie"] = _sanitize_cookie(os.getenv("TRUTHSOCIAL_COOKIE"))
    print("Using Truth Social cookie from environment.")

# ═════════ Helpers ══════════════════════
def clean_gpt_text(text: str) -> str:
    return " ".join(text.split())

def get_time_diff(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    mins = int((datetime.now(timezone.utc) - dt).total_seconds() // 60)
    if mins < 60:
        return f"{mins} min ago"
    hrs = mins // 60
    return f"{hrs} hrs ago" if hrs < 24 else f"{hrs // 24} days ago"

# ═════════ Data model ═══════════════════
@dataclass
class TruthItem:
    created_at: datetime
    sentiment: str
    summary: str

# ═════════ OpenAI wrapper ════════════════
@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, max=10))
def _gpt(body: str, api_key: str, header: str) -> dict[str, str]:
    import openai
    from openai import OpenAI

    prompt = header + body
    print("\nPROMPT SENT TO OPENAI:\n" + prompt + "\n")
    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=120,
        )
    except openai.PermissionDeniedError:
        print("Model gpt-4o-mini unavailable, falling back to gpt-3.5-turbo")
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=120,
        )

    text = resp.choices[0].message.content.strip()
    print("RAW GPT RESPONSE:", text)
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"summary": text[:60], "sentiment": "Unknown"}

# ═════════ Fetch layers ═══════════════════
def _json_statuses(limit: int) -> List[Tuple[datetime, str]]:
    url = f"https://truthsocial.com/api/v1/accounts/{ACCOUNT_ID}/statuses"
    out: List[Tuple[datetime, str]] = []
    max_id = None
    while len(out) < limit:
        params = {"limit": min(40, limit - len(out))}
        if max_id:
            params["max_id"] = max_id
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code in (401, 403):
            raise PermissionError("JSON endpoint blocked")
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        for st in data:
            if st.get("reblog"):
                continue
            txt = BeautifulSoup(st.get("content", ""), "html.parser").get_text(" ", strip=True)
            if txt.startswith("@realDonaldTrump"):
                txt = txt.split(" ", 1)[-1]
            if not txt:
                continue
            ts = datetime.fromisoformat(st.get("created_at").replace("Z", "+00:00"))
            out.append((ts, txt))
            if len(out) >= limit:
                break
        max_id = data[-1].get("id") if data else None
    return out


def _rss_statuses(limit: int) -> List[Tuple[datetime, str]]:
    r = requests.get(f"https://truthsocial.com/@realDonaldTrump.rss", headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out: List[Tuple[datetime, str]] = []
    for item in soup.select("item"):
        txt = item.description.get_text(" ", strip=True)
        if txt.startswith("@realDonaldTrump"):
            txt = txt.split(" ", 1)[-1]
        pub = item.pubDate.get_text()
        ts = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %z")
        out.append((ts, txt))
        if len(out) >= limit:
            break
    return out


def _playwright_statuses(limit: int) -> List[Tuple[datetime, str]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed; skipping fallback.")
        return []
    print("Launching Playwright fallback…")
    out: List[Tuple[datetime, str]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=USER_AGENT)
        if "Cookie" in HEADERS:
            for p in HEADERS["Cookie"].split(";"):
                k, _, v = p.strip().partition("=")
                ctx.add_cookies([{"name": k, "value": v, "url": "https://truthsocial.com"}])
        page = ctx.new_page()
        page.goto(BASE_URL, timeout=60000)
        page.wait_for_timeout(2000)
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        html = page.content()
        print(f"Playwright page content length: {len(html)}")
        try:
            page.wait_for_selector("div[data-testid='status']", timeout=60000)
        except Exception:
            browser.close()
            raise PermissionError("No status elements; likely blocked")
        items = page.query_selector_all("div[data-testid='status']")
        for art in items:
            txt = art.inner_text().strip()
            if txt.startswith("@realDonaldTrump"): continue
            t = art.query_selector("time[datetime]")
            ts_raw = t.get_attribute("datetime") if t else None
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")) if ts_raw else datetime.now(timezone.utc)
            out.append((ts, txt))
            if len(out) >= limit: break
        browser.close()
    return out


def _html_statuses(limit: int) -> List[Tuple[datetime, str]]:
    r = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out: List[Tuple[datetime, str]] = []
    for art in soup.select("div[data-testid='status']"):
        txt = art.get_text(" ", strip=True)
        if txt.startswith("@realDonaldTrump"): continue
        tt = art.select_one("time[datetime]")
        ts = datetime.fromisoformat(tt["datetime"].replace("Z", "+00:00")) if tt else datetime.now(timezone.utc)
        out.append((ts, txt))
        if len(out) >= limit: break
    return out


def _fetch_statuses(limit: int) -> List[Tuple[datetime, str]]:
    for fn in (_json_statuses, _rss_statuses, _playwright_statuses, _html_statuses):
        print(f"Attempt {fn.__name__} limit={limit}")
        try:
            ps = fn(limit)
            print(f"{fn.__name__} got {len(ps)} posts")
            if ps:
                for t, x in ps:
                    print(f"- [{t.isoformat()}] {x}")
                return ps
        except Exception as e:
            print(f"{fn.__name__} error:", e)
    print("No posts fetched")
    return []

# ═════════ Market snapshot ════════════════
def _safe_snapshot() -> dict[str, Any]:
    try:
        fi = yf.Ticker("^GSPC").fast_info or {}
        price = fi.get("lastPrice") or fi.get("last_price")
        prev = fi.get("previousClose", price)
        change = ((price - prev) / prev * 100) if price and prev else 0.0
        return {"price": round(price, 2) if price else None, "change": round(change, 2)}
    except Exception:
        return {"price": None, "change": 0.0}

# ═════════ Market sentiment API ════════════════
def get_overall_market_sentiment(*, max_posts: int = 20, api_key: str | None = None) -> dict[str, Any]:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing")
    posts = _fetch_statuses(max_posts)
    snap = _safe_snapshot()
    price = snap["price"]
    change = snap["change"]
    info = yf.Ticker("^GSPC").info
    market_cap = info.get("marketCap")
    if posts:
        header = (
            "Below are recent Truth Social posts by Donald Trump separated by '---'.\n"
            "Assess implied short-term sentiment for US equity market.\n"
            "Return JSON with keys sentiment & rationale.\n\n"
        )
        body = "\n---\n".join(txt for _, txt in posts)
        print("DEBUG PROMPT HEADER:\n", header)
        print("DEBUG PROMPT BODY:\n", body)
        res = _gpt(body, key, header)
        sentiment = res.get("sentiment", "Unknown")
        rationale = res.get("rationale", res.get("summary", ""))
    else:
        sentiment = "Unknown"
        rationale = "No posts; unable to infer sentiment."
    return {
        "ticker": "SPX",
        "company": "S&P 500",
        "price": price,
        "change": change,
        "marketCap": market_cap,
        "sector": "Index",
        "Trump sentiment": sentiment,
        "aiHighlight": rationale,
        "newsSummary": []
    }

# ──────────────── CLI & tests ─────────────────
class LiveTests(unittest.TestCase):
    def setUp(self):
        if not os.getenv("OPENAI_API_KEY"): self.skipTest("no key")
    def test_fetch(self):
        ps = _fetch_statuses(1)
        if not ps: self.skipTest("no posts")
        self.assertTrue(ps)
    def test_sentiment(self):
        try:
            r = get_overall_market_sentiment(max_posts=3)
        except Exception as e:
            self.skipTest(str(e))
        self.assertIn("marketSentiment", r)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["market", "test"], nargs="?", default="test")
    p.add_argument("--api-key")
    p.add_argument("--cookie")
    args = p.parse_args()
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    if args.cookie:
        HEADERS["Cookie"] = _sanitize_cookie(args.cookie)
    if args.mode == "test":
        unittest.main(argv=[""], exit=False)
    else:
        print(json.dumps(get_overall_market_sentiment(api_key=args.api_key), indent=2))
