import yfinance as yf
import pandas as pd
import time

companies = ["ZEN", "TWLO", "PD", "BOX", "TDOC", "AMWL", "HIMS", "MAN", "RHI", "ASGN"]
portfolio_data = {}

for ticker in companies:
    stock = yf.Ticker(ticker)
    
    income_stmt = stock.financials
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow

    # Print warnings if financial data is empty
    if income_stmt.empty and balance_sheet.empty and cash_flow.empty:
        print(f"Warning: No financial data found for {ticker}. Skipping...")
        continue  

    portfolio_data[ticker] = {
        "Income Statement": income_stmt,
        "Balance Sheet": balance_sheet,
        "Cash Flow": cash_flow
    }

    print(f"Fetched data for {ticker}")
    time.sleep(2)  

for ticker, data in portfolio_data.items():
    if not data["Income Statement"].empty:
        data["Income Statement"].to_csv(f"data/{ticker}_income.csv")
    if not data["Balance Sheet"].empty:
        data["Balance Sheet"].to_csv(f"data/{ticker}_balance.csv")
    if not data["Cash Flow"].empty:
        data["Cash Flow"].to_csv(f"data/{ticker}_cash.csv")

print("Data saved to CSV files")
