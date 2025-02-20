import pandas as pd
import yfinance as yf
from tqdm import tqdm
import requests
from pandas.tseries.offsets import BDay
import base64
import json
import os

# Function to update the data and push to GitHub
def update_data():
    # Load the dataset from GitHub URL
    csv_file_url = 'https://raw.githubusercontent.com/Kimnguyenwork85/tariff_dashboard/main/dashboard_source_data.csv'
    df = pd.read_csv(csv_file_url)
    df = df[['Ticker', 'Industry', 'Company']]  # Select only the relevant columns
    # Define the date range
    end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    start_date = (pd.Timestamp.today() - pd.DateOffset(years=2)).strftime('%Y-%m-%d')

    # Initialize an empty DataFrame
    all_data = []

    # Loop through tickers and fetch data
    for index, row in df.iterrows():
        ticker = row['Ticker']
        Industry = row['Industry']
        Company = row['Company']
        ticker_data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)[["Close", "High", "Low", "Open", "Volume"]]
        ticker_data = ticker_data.reset_index()
        ticker_data.columns = ticker_data.columns.droplevel(1)  # Remove multi-level columns
        ticker_data['Date'] = pd.to_datetime(ticker_data['Date']).dt.date
        ticker_data["Ticker"] = ticker
        ticker_data["Industry"] = Industry
        ticker_data["Company"] = Company
        all_data.append(ticker_data)

    # Combine all data into a single DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)

    # Calculate current price, 1-day return, 7-day return, 30-day return, 6-month return, and additional metrics for each ticker
    results = []

    for ticker in combined_data['Ticker'].unique():
        ticker_data = combined_data[combined_data['Ticker'] == ticker]
        
        # Current price
        current_price = ticker_data['Close'].iloc[-1]
        
        # 1-day return (Yesterday)
        price_1d_ago = ticker_data['Close'].shift(1).iloc[-1]
        return_1d = ((current_price - price_1d_ago) / price_1d_ago) * 100 if price_1d_ago else None
        
        # 7-day return
        price_7d_ago = ticker_data['Close'].shift(7).iloc[-1]
        return_7d = ((current_price - price_7d_ago) / price_7d_ago) * 100 if price_7d_ago else None
        
        # 30-day return
        price_30d_ago = ticker_data['Close'].shift(30).iloc[-1]
        return_30d = ((current_price - price_30d_ago) / price_30d_ago) * 100 if price_30d_ago else None
        
        # 6-month return
        price_6m_ago = ticker_data['Close'].shift(180).iloc[-1]
        return_6m = ((current_price - price_6m_ago) / price_6m_ago) * 100 if price_6m_ago else None
        
        # Fetch additional metrics
        ticker_info = yf.Ticker(ticker).info
        pe_ratio = ticker_info.get('trailingPE', None)
        market_cap = ticker_info.get('marketCap', None)
        short_ratio = ticker_info.get('shortRatio', None)
        forward_pe = ticker_info.get('forwardPE', None)
        
        # Append the results
        results.append({
            'Ticker': ticker,
            'Current Price (USD)': current_price,
            '1-Day Return (%)': return_1d,
            '7-Day Return (%)': return_7d,
            '30-Day Return (%)': return_30d,
            '6-Month Return (%)': return_6m,
            'P/E Ratio': pe_ratio,
            'Market Cap': market_cap,
            'Short Ratio': short_ratio,
            'Forward P/E': forward_pe
        })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    final_df = pd.merge(df, results_df, on='Ticker', how='left')

    # Convert final_df to CSV
    csv_data = final_df.to_csv(index=False)

    # GitHub repository details
    repo = "Kimnguyenwork85/tariff_dashboard"
    path = "dashboard_source_data.csv"
    branch = "main"
    API_TOKEN = os.getenv('TARIFF_GITHUB_TOKEN')

    # Get the SHA of the existing file
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {API_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        sha = response_json['sha']
    else:
        sha = None

    # Update or create the file on GitHub
    update_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    data = {
        "message": "Update dashboard_source_data.csv",
        "content": base64.b64encode(csv_data.encode()).decode(),
        "branch": branch
    }
    if sha:
        data["sha"] = sha

    response = requests.put(update_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("File updated successfully.")
    else:
        print(f"Failed to update file: {response.status_code}")
        print(response.json())

# Run the update function
if __name__ == "__main__":
    update_data()