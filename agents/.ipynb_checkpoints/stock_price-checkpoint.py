import yfinance as yf
import requests
def fetch_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return f"📈 {ticker}: ${price:.2f}"
    except Exception:
        return f"❌ Unable to fetch stock price for '{ticker}'."
