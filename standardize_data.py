import pandas as pd
import os

companies = ["TWLO", "PD", "BOX", "TDOC", "AMWL", "HIMS", "MAN", "RHI", "ASGN"]

data_folder = "data"

standardized_data = {
    "Company": [],
    "Revenue": [],
    "EBITDA": [],
    "Total Debt": [],
    "Interest Expense": [],
    "Cash Flow from Operations": []
}

def get_latest_value(df, metric):
    # Transpose to get dates as rows, metrics as columns
    df = df.T
    # Take the most recent year (first row after transpose)
    if metric in df.columns and not pd.isna(df[metric].iloc[0]):
        return df[metric].iloc[0]
    return None

for ticker in companies:
    try:
        income = pd.read_csv(f"{data_folder}/{ticker}_income.csv", index_col=0)
        balance = pd.read_csv(f"{data_folder}/{ticker}_balance.csv", index_col=0)
        cash_flow = pd.read_csv(f"{data_folder}/{ticker}_cash.csv", index_col=0)

        revenue = get_latest_value(income, "Total Revenue")
        ebitda = get_latest_value(income, "EBITDA")  # May not always be present
        total_debt = get_latest_value(balance, "Total Debt")
        interest_expense = get_latest_value(income, "Interest Expense")
        cash_flow_ops = get_latest_value(cash_flow, "Operating Cash Flow")

        if ebitda is None and "Operating Income" in income.index and "Depreciation & Amortization" in income.index:
            op_income = get_latest_value(income, "Operating Income")
            depreciation = get_latest_value(income, "Depreciation & Amortization")
            if op_income and depreciation:
                ebitda = op_income + depreciation

        standardized_data["Company"].append(ticker)
        standardized_data["Revenue"].append(revenue)
        standardized_data["EBITDA"].append(ebitda)
        standardized_data["Total Debt"].append(total_debt)
        standardized_data["Interest Expense"].append(abs(interest_expense) if interest_expense else None)  # Ensure positive
        standardized_data["Cash Flow from Operations"].append(cash_flow_ops)

        print(f"Processed data for {ticker}")
    except Exception as e:
        print(f"Error processing {ticker}: {e}")

portfolio_df = pd.DataFrame(standardized_data)

numeric_cols = ["Revenue", "EBITDA", "Total Debt", "Interest Expense", "Cash Flow from Operations"]
for col in numeric_cols:
    portfolio_df[col] = pd.to_numeric(portfolio_df[col], errors="coerce")

portfolio_df.to_csv("data/standardized_portfolio.csv", index=False)
print("Standardized data saved to 'standardized_portfolio.csv'")
print(portfolio_df)
