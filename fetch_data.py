import yfinance as yf
import pandas as pd

companies = ["ZEN", "TWLO", "PD", "BOX", "TDOC", "AMWL", "HIMS", "MAN", "RHI", "ASGN"]

portfolio_data = {}

for ticker in companies:
    stock = yf.Ticker(ticker)
    # Get income statement, balance sheet, and cash flow (annual data)
    income_stmt = stock.financials
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    portfolio_data[ticker] = {
        "Income Statement": income_stmt,
        "Balance Sheet": balance_sheet,
        "Cash Flow": cash_flow
    }
    print(f"Fetched data for {ticker}")

for ticker, data in portfolio_data.items():
    data["Income Statement"].to_csv(f"data/{ticker}_income.csv")
    data["Balance Sheet"].to_csv(f"data/{ticker}_balance.csv")
    data["Cash Flow"].to_csv(f"data/{ticker}_cash.csv")
print("Data saved to CSV files")
