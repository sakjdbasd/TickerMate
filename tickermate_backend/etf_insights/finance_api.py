import yfinance as yf

def get_etf_profile(ticker):
    etf = yf.Ticker(ticker)
    info = etf.info
    fast_info = etf.fast_info

    last_price = fast_info["lastPrice"]
    previous_close = fast_info["previousClose"]

    change = (last_price - previous_close) / previous_close * 100
    # return info
    return {
        "ticker": ticker,
        "name": info.get("shortName"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "price": str(round(last_price,2)),
        "previous_close": str(round(previous_close,2)),
        "change": str(round(change,2)) + "%",
    }

if __name__ == "__main__":
    print(get_etf_profile("MSFT"))

