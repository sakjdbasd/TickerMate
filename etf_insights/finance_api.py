import yfinance as yf

def get_etf_profile(ticker):
    etf = yf.Ticker(ticker)
    info = etf.info
    # return info
    return {
        "name": info.get("shortName"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "expense_ratio": info.get("annualReportExpenseRatio"),
        "dayLow": info.get("dayLow"),
        "dayHigh": info.get("dayHigh"),
        "beta": info.get("beta"),
        "trailingPE": info.get("trailingPE"),
        "totalAssets": info.get("totalAssets"),
        "navPrice": info.get("navPrice"),
    }

def get_etf_history(ticker, period="1y"):
    etf = yf.Ticker(ticker)
    return etf.history(period=period)

def print_all_info_fields(ticker):
    etf = yf.Ticker(ticker)
    info = etf.info

    print(f" {len(info)} fields:")
    for i, key in enumerate(sorted(info.keys()), 1):
        print(f"{i:02d}. {key}")

# if __name__ == "__main__":
    # print(get_etf_profile("AAPL"))
    # print(get_etf_history("AAPL"))
    # print_all_info_fields("AAPL")
