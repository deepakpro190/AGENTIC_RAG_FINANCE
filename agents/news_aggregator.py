import requests

import streamlit as st
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

'''def fetch_financial_news():
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
'''

def fetch_financial_news():
    """
    Fetches the latest financial news articles.
    :return: List of dictionaries with article details (title, source, URL, content).
    """
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        news_data = response.json()

        if news_data.get("status") == "ok" and "articles" in news_data:
            articles = news_data["articles"][:5]  # Get up to 5 articles
            
            if not articles:
                return None  # No news available
            
            # Extract necessary details
            news_list = []
            for article in articles:
                news_list.append({
                    "title": article.get("title", "No title"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", "#"),
                    "content": article.get("description", "No description available."),
                })
            
            return news_list

        return None  # No valid news data found

    except requests.exceptions.RequestException as e:
        return None  # Return None if API fails
