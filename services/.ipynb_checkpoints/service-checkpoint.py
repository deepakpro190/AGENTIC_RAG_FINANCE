import requests
import streamlit as st
import requests


import yfinance as yf
from datetime import datetime
import sys
sys.path.append('services')

from config import (
    NEWS_API_KEY,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    StockAPIClient,
    SEC_BASE_URL,
)

# --- Function Definitions ---

def fetch_wikipedia_info(query, limit=1):
    try:
        # Construct the Wikipedia API endpoint URL
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&titles={query}&prop=extracts&exintro&explaintext"
        
        # Send the GET request to the Wikipedia API
        response = requests.get(url)
        
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        
        # Parse the response as JSON
        data = response.json()
        
        # Extract the page content
        pages = data.get("query", {}).get("pages", {})
        
        # If there are results, format them into readable information
        result = []
        for page_id, page_info in pages.items():
            title = page_info.get("title", "No title")
            extract = page_info.get("extract", "No extract available")
            result.append(f"Title: {title}\nContent: {extract}")
        
        # Limit the number of results
        return result[:limit]

    except Exception as e:
        print(f"Error fetching Wikipedia data: {e}")
        return []


def fetch_reddit_posts(query, limit=10):
    try:
        url = f"https://www.reddit.com/search.json?q={query}&limit={limit}"
        headers = {"User-Agent": REDDIT_USER_AGENT}
        auth = (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        data = response.json()
        return [
            f"Title: {item['data']['title']}\nContent: {item['data']['selftext']}" 
            for item in data.get("data", {}).get("children", [])
        ]
    except Exception as e:
        st.error(f"Error fetching Reddit data: {e}")
        return []


def fetch_sec_filings(company, limit=5):
    try:
        url = f"{SEC_BASE_URL}/company/{company}/filings?limit={limit}"
        response = requests.get(url)
        response.raise_for_status()
        filings = response.json()
        return [f"Filing: {filing['title']} Date: {filing['date']}" for filing in filings]
    except Exception as e:
        st.error(f"Error fetching SEC data: {e}")
        return []


def fetch_news_articles(query, limit=5):
    try:
        url = f"https://newsapi.org/v2/everything?q={query}&pageSize={limit}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return [f"Title: {article['title']} Source: {article['source']['name']}" for article in articles]
    except Exception as e:
        st.error(f"Error fetching news data: {e}")
        return []


def fetch_stock_data(stock_symbol, date=None):
    # Default to today's date if no date is provided
    if date is None:
        date = datetime.today().date()
    
    # Fetch the stock data for the symbol
    stock_data = yf.Ticker(stock_symbol)
    
    # If a specific date is provided, fetch data for that date
    if date != datetime.today().date():
        stock_data_history = stock_data.history(period="1d", start=date, end=date)
        if stock_data_history.empty:
            raise ValueError(f"No data found for {stock_symbol} on {date}")
        return stock_data_history
    else:
        # Otherwise, fetch the latest stock data
        stock_data_history = stock_data.history(period="1d")
        return stock_data_history
