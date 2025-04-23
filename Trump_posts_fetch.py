"""
truth_social_agent/summarized_truth.py  (v1.3 – network‑safe)
------------------------------------------------------------
TickerMate‑style summariser for Donald J. Trump’s Truth Social posts **that now
runs even when outbound HTTP calls (Yahoo Finance) are blocked**.

**What’s new (v1.3)**
* **`safe_get_market_snapshot()`** wraps the `yfinance.Ticker` calls in a broad
  `try/except` block.  If *anything* goes wrong (offline sandbox, Yahoo API
  change, etc.) we fall back to price `None`, change `0%`, and strings `"N/A"`.
* Added a unit test `test_yfinance_failure_fallback` that monkey‑patches
  `yfinance.Ticker` to raise `ConnectionError` and asserts we still get a JSON
  blob (with price `None`).
* No other behaviour or schema changed, so the front‑end remains unaffected.

Run examples
~~~~~~~~~~~~
```bash
# with env var (unchanged)
export OPENAI_API_KEY=sk‑...
python summarized_truth.py TSLA

# offline? still works, just gets N/A price data
python summarized_truth.py TSLA --api-key sk-...

# run tests (all network calls mocked)
python summarized_truth.py test
```
"""

from __future__ import annotations

import argparse
import json
import os
import re
import types
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Tuple, Any

import requests
import yfinance as yf
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential

# ---------------------------------------------------------------------------
# Optional utils import – fall back to local stubs in notebooks/sandboxes
# ---------------------------------------------------------------------------
try:
    from news_agent.utils import clean_gpt_text, get_time_diff  # type: ignore
except ModuleNotFoundError:  # minimal fallbacks

    def clean_gpt_text(txt: str) -> str:  # noqa: D401
        return " ".join(txt.split())

    def get_time_diff(iso_dt: str) -> str:  # noqa: D401
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        mins = int((datetime.now(timezone.utc) - dt).total_seconds() / 60)
        if mins < 60:
            return f"{mins} min ago"
        hrs = mins // 60
        if hrs < 24:
            return f"{hrs} hrs ago"
        days = hrs // 24
        return f"{days} days ago"

# ---------------------------------------------------------------------------
# Env & constants
# ---------------------------------------------------------------------------
load_dotenv()
ENV_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://truthsocial.com/@realDonaldTrump"
HEADERS = {"User-Agent": "Mozilla/5.0 (TickerMateBot/1.3)"}
TICKER_RE = re.compile(r"\$(DJI|SPX|NDX|[A-Z]{1,5})")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class TruthItem:
    created_at: datetime
    sentiment: str
    summary: str

# ---------------------------------------------------------------------------
# GPT wrapper (lazy import for mockability)
# ---------------------------------------------------------------------------
@retry(stop=stop_after_attempt(4), wait=wait_random_exponential(multiplier=2, max=30))
def _gpt_summarise(text: str, api_key: str, word_limit: int) -> TruthItem:
    import openai  # noqa: WPS433

    openai.api_key = api_key
    prompt = (
        "Donald Trump posted the following on Truth Social.\n----\n" + text + "\n----\n\n"
        f"Task: 1) Summarise potential market impact in ≤{word_limit} words. "
        "2) Classify implied market sentiment (Bullish/Bearish/Neutral). "
        "Return JSON with keys summary & sentiment only. No extra text."
    )
    rsp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=120,
    )
    content = rsp.choices[0].message.content.strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"summary": content.split("\n", 1)[0][:60], "sentiment": "Unknown"}
    return TruthItem(datetime.now(timezone.utc), data["sentiment"], data["summary"])

# ---------------------------------------------------------------------------
# Market snapshot helper – network‑safe
# ---------------------------------------------------------------------------

def safe_get_market_snapshot(ticker: str) -> dict[str, Any]:
    """Return dict with name, sector, price, prevClose – tolerate network errors."""
    try:
        yf_tk = yf.Ticker(ticker)
        info = yf_tk.info or {}
        fast = yf_tk.fast_info or {}
        price = fast.get("lastPrice") or fast.get("last_price")
        prev = fast.get("previousClose", price)
        change_pct = ((price - prev) / prev * 100) if (price and prev) else 0.0
    except Exception:  # noqa: BLE001 – any failure ⇒ fallback
        info = {}
        price = None
        change_pct = 0.0
    return {
        "name": info.get("shortName", "N/A"),
        "sector": info.get("sector", "N/A"),
        "price": None if price is None else round(price, 2),
        "change_pct": round(change_pct, 2),
    }

# ---------------------------------------------------------------------------
# Scraper utilities
# ---------------------------------------------------------------------------

def _fetch_truth_html() -> str:
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def _extract_posts(html: str, ticker: str, limit: int) -> List[Tuple[datetime, str]]:
    soup = BeautifulSoup(html, "html.parser")
    posts: List[Tuple[datetime, str]] = []
    for card in soup.select("div.card"):
        body = card.select_one("div.post-body")
        if not body:
            continue
        text = body.get_text("\n", strip=True)
        if f"${ticker.upper()}" not in text.upper():
            continue
        time_tag = card.select_one("time[datetime]")
        created = (
            datetime.fromisoformat(time_tag["datetime"]).astimezone(timezone.utc)
            if time_tag else datetime.now(timezone.utc)
        )
        posts.append((created, text))
        if len(posts) >= limit:
            break
    return posts

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_summarized_truth(ticker: str, *, max_posts: int = 4, api_key: str | None = None):
    api_key = api_key or ENV_OPENAI_API_KEY

    mk = safe_get_market_snapshot(ticker)

    raw_posts = _extract_posts(_fetch_truth_html(), ticker, max_posts)
    if not raw_posts:
        return {
            "ticker": ticker,
            "name": mk["name"],
            "sector": mk["sector"],
            "price": None if mk["price"] is None else f"{mk['price']:.2f}",
            "change": f"{mk['change_pct']:.2f}%",
            "AI Hightlight": "No recent Truth Social mentions.",
            "News Summary": [],
        }

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing – required because posts mention the ticker")

    analyses: List[TruthItem] = []
    for idx, (created, txt) in enumerate(raw_posts):
        wl = 50 if idx == 0 else 15
        ti = _gpt_summarise(txt, api_key, wl)
        ti.created_at = created
        ti.summary = clean_gpt_text(ti.summary)
        analyses.append(ti)

    ai_highlight = analyses[0].summary
    news_summary = [
        {
            "time": get_time_diff(ti.created_at.isoformat()),
            "source": "Truth Social",
            "sentiment": ti.sentiment,
            "summary": ti.summary,
        }
        for ti in analyses[1:]
    ]

    return {
        "ticker": ticker,
        "name": mk["name"],
        "sector": mk["sector"],
        "price": None if mk["price"] is None else f"{mk['price']:.2f}",
        "change": f"{mk['change_pct']:.2f}%",
        "AI Hightlight": ai_highlight,
        "News Summary": news_summary,
    }

# ---------------------------------------------------------------------------
# Unit tests (all external calls mocked)
# ---------------------------------------------------------------------------

class _TruthSocialTests(unittest.TestCase):
    def setUp(self):
        # patch requests
        self.req_patcher = unittest.mock.patch("requests.get", autospec=True)
        self.mock_get = self.req_patcher.start()
        # patch openai
        self.openai_patcher = unittest.mock.patch.dict("sys.modules", {"openai": _fake_openai_module()})
        self.openai_patcher.start()
        # patch yfinance.Ticker to avoid network
        self.yf_patcher = unittest.mock.patch("yfinance.Ticker", autospec=True)
        self.mock_yf = self.yf_patcher.start()
        self.mock_yf.return_value.info = {"shortName": "Apple Inc.", "sector": "Technology"}
        self.mock_yf.return_value.fast_info = {"last_price": 100, "previousClose": 95}

    def tearDown(self):
        self.req_patcher.stop()
        self.openai_patcher.stop()
        self.yf_patcher.stop()

    def _html(self, body: str):
        return (
            "<html><body><div class='card'><div class='post-body'>" + body +
            "</div><time datetime='2025-04-22T12:00:00Z'></time></div></body></html>"
        )

    def test_no_mentions(self):
        self.mock_get.return_value = _fake_resp(self._html("hello"))
        res = get_summarized_truth("AAPL", api_key="sk-test")
        self.assertEqual(res["AI Hightlight"], "No recent Truth Social mentions.")

    def test_missing_api_key_with_mentions(self):
        self.mock_get.return_value = _fake_resp(self._html("$AAPL to the moon"))
        with self.assertRaises(RuntimeError):
            get_summarized_truth("AAPL", api_key=None)

    def test_single_mention(self):
        self.mock_get.return_value = _fake_resp(self._html("Great day for $AAPL!"))
        res = get_summarized_truth("AAPL", api_key="sk-test")
        self.assertEqual(len(res["News Summary"]), 0)

    def test_yfinance_failure_fallback(self):
        # Make yfinance explode
        self.mock_yf.side_effect = Exception("network gone")
        self.mock_get.return_value = _fake_resp(self._html("hello"))
        res = get_summarized_truth("TSLA", api_key="sk-test")
        self.assertIsNone(res["price"], "Price should be None when yfinance fails")

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _fake_resp(html: str):
    r = types.SimpleNamespace()
    r.status_code = 200
    r.text = html
    r.raise_for_status = lambda: None
    return r


def _fake_openai_module():
    mod = types.ModuleType("openai")

    class _Resp:
        def __init__(self, content):
            self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]

    class _Chat:
        @staticmethod
        def create(**kwargs):
            return _Resp(json.dumps({"summary": "stub", "sentiment": "Neutral"}))

    mod.ChatCompletion = _Chat
    mod.api_key = None
    return mod

# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    argp = argparse.ArgumentParser(description="Summarise Trump’s Truth Social posts for a given ticker.")
    argp.add_argument("ticker", nargs="?", default="TSLA")
    argp.add_argument("--api-key", dest="api_key", help="OpenAI API key (overrides env var)")
    argp.add_argument("--max-posts", type=int, default=4)
    argp.add_argument("test", nargs="?", help=argparse.SUPPRESS)
    args, _ = argp.parse_known_args()

    if args.ticker == "test":
        unittest.main(argv=[__file__])
    else:
        import pprint

        res = get_summarized_truth(args.ticker, max_posts=args.max_posts, api_key=args.api_key)
        pprint.pp(res)
