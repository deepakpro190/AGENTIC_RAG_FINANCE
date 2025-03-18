import requests
import json
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

def analyze_query_with_llm(user_query):
    try:
        chat_context = [
            {"role": "system", "content": """You are a financial AI assistant.
                - Identify if the query is about stock prices, comparisons, or finance news.
                - Extract company names & stock tickers.
                - Return JSON: {"query_type": "stock_price" | "compare" | "news", "companies": [{"name": "Tesla", "ticker": "TSLA"}]}"""},
            {"role": "user", "content": user_query}
        ]

        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={"model": "open-mistral-7b", "messages": chat_context, "max_tokens": 200}
        )

        return json.loads(response.json()["choices"][0]["message"]["content"])
    except Exception:
        return {"query_type": "general", "companies": []}
