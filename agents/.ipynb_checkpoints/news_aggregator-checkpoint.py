import requests

import streamlit as st
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

def fetch_financial_news():
    """
    Fetches latest financial news headlines.
    :return: List of top financial news headlines
    """
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        news_data = response.json()

        if news_data["status"] == "ok":
            headlines = [f"📰 {article['title']} - [{article['source']['name']}]({article['url']})" for article in news_data["articles"][:5]]
            return "\n\n".join(headlines)
        else:
            return "❌ Error fetching news."
    except Exception as e:
        return f"❌ News API Error: {str(e)}"
