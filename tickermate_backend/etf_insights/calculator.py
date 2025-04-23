import math 

def simulate_dividend_growth(principal, annual_yield, years):     
    result = []     
    for year in range(1, years+1):         
        value = principal * (1 + annual_yield) ** year         
        result.append((year, round(value, 2)))     
    return result

def suggest_account_type(ticker, dividend_type):     
    if dividend_type == 'US':         
        return "RRSP is more suitable and is exempt from US dividend tax"     
    else:         
        return "TFSA is the best choice as all income can be tax-free"

if __name__ == "__main__":
    print(simulate_dividend_growth(1000,0.05,5))