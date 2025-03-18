import pandas as pd

portfolio_df = pd.read_csv("data/standardized_portfolio.csv")

portfolio_df["Leverage Ratio"] = portfolio_df["Total Debt"] / portfolio_df["EBITDA"]

def calculate_interest_coverage(row):
    if row["Interest Expense"] == 0:
        return 1000 if row["EBITDA"] >= 0 else -1000  # High positive/negative value for no debt
    return row["EBITDA"] / row["Interest Expense"]

portfolio_df["Interest Coverage"] = portfolio_df.apply(calculate_interest_coverage, axis=1)

portfolio_df["EBITDA Margin"] = portfolio_df["EBITDA"] / portfolio_df["Revenue"]

def categorize_company(row):
    leverage = row["Leverage Ratio"]
    interest_coverage = row["Interest Coverage"]
    ebitda_margin = row["EBITDA Margin"]

    if row["EBITDA"] < 0:
        return "Red" 

    if leverage < 3 and interest_coverage > 5 and ebitda_margin > 0.15:
        return "Green"
    elif (3 <= leverage <= 4 or 3 <= interest_coverage <= 5 or 0.05 <= ebitda_margin <= 0.15):
        return "Yellow"
    elif (4 < leverage <= 5 or 2 <= interest_coverage < 3 or ebitda_margin < 0.05):
        return "Amber"
    else:
        return "Red"

portfolio_df["Category"] = portfolio_df.apply(categorize_company, axis=1)

portfolio_df.to_csv("data/analyzed_portfolio.csv", index=False)
print("Analyzed data saved to 'analyzed_portfolio.csv'")
print(portfolio_df)
