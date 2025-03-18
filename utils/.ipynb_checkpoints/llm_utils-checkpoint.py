import requests
import json
from config import MISTRAL_API_KEY

def call_llm(chat_context):
    """
    Calls Mistral AI model with provided chat history.
    :param chat_context: List of messages [{"role": "user", "content": "query"}]
    :return: LLM response text
    """
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={"model": "open-mistral-7b", "messages": chat_context, "max_tokens": 200}
        )

        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ LLM Error: {str(e)}"
