import torch
import chromadb
import streamlit as st
import speech_recognition as sr
import requests
import tempfile
from gtts import gTTS
import os
import yfinance as yf  # ✅ New addition for stock price fetching
import re
from io import BytesIO
import spacy

# ✅ Load spaCy NER model (make sure you've installed it!)
nlp = spacy.load("en_core_web_lg")
# ✅ ChromaDB Setup
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="finance_docs")

# ✅ Force GPU if available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ✅ API Key for Mistral
MISTRAL_API_KEY = ""  # Replace with your actual API key

# ✅ Streamlit UI
st.set_page_config(page_title="💰 Finance RAG AI", layout="wide")
st.title("💰 Finance RAG AI - Chat Mode")

# ✅ Initialize session state for chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores full chat history

if "user_query" not in st.session_state:
    st.session_state.user_query = ""  # Stores ongoing user query

# ✅ Function to handle voice input
def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.sidebar.write("🗣️ Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source)  # Noise reduction
        
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)  # Increased timeout
            query = recognizer.recognize_google(audio)  # Convert to text
            return query
        except sr.WaitTimeoutError:
            st.sidebar.error("⏳ No speech detected. Please try again.")
        except sr.UnknownValueError:
            st.sidebar.error("❌ Could not understand the audio.")
        except sr.RequestError:
            st.sidebar.error("❌ Speech recognition service unavailable.")
    return ""

# ✅ Retrieve documents from ChromaDB
def query_chromadb(user_query):
    results = collection.query(query_texts=[user_query], n_results=3)
    return results['documents'][0] if results['documents'] else []


# ✅ Function to call LLM for query analysis, company detection & ticker retrieval
def analyze_query_with_llm(user_query):
    """
    Calls Mistral LLM to:
    - Determine query type (stock_price / general).
    - Extract company/organization names.
    - Provide corresponding stock ticker symbols.
    """
    try:
        chat_context = [
            {"role": "system", "content": """You are a financial AI assistant.
                - Detect if the user query is related to stock prices or general finance.
                - Extract company/brand names from the query.
                - Provide their respective stock ticker symbols.
                - If no valid company/ticker is found, return 'None'.
                
                Your response should be in JSON format:
                {"query_type": "stock_price" or "general", "companies": [{"name": "Tesla", "ticker": "TSLA"}, {"name": "Apple", "ticker": "AAPL"}]}
            """},
            {"role": "user", "content": user_query}
        ]

        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={
                "model": "open-mistral-7b",
                "messages": chat_context,
                "max_tokens": 200,
                "temperature": 0.3,
                "top_p": 1,
                "stream": False,
            },
        )

        response_json = response.json()
        llm_result = response_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # ✅ Convert response to JSON
        import json
        llm_data = json.loads(llm_result)

        return llm_data  # Expected format: {"query_type": "stock_price", "companies": [{"name": "Tesla", "ticker": "TSLA"}]}

    except Exception as e:
        return {"query_type": "general", "companies": []}

# ✅ Function to fetch stock price
def fetch_stock_price(ticker):
    """
    Fetches the latest stock price for a given ticker symbol.
    """
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return f"The latest stock price of {ticker} is **${price:.2f}**."
    except Exception as e:
        return f"❌ Unable to fetch stock price for '{ticker}'. Error: {str(e)}"


# ✅ Generate Response using Mistral API with Chat History
def generate_response(query):
    llm_result = analyze_query_with_llm(user_query)

    query_type = llm_result.get("query_type", "general")
    companies = llm_result.get("companies", [])
    if query_type == "stock_price":
        if not companies:
            return "❌ No company names detected. Please specify a valid company."

        response_messages = []
        for company in companies:
            name = company.get("name")
            ticker = company.get("ticker")
            if ticker:
                stock_price = fetch_stock_price(ticker)
                response_messages.append(f"📈 **{name} ({ticker})**: {stock_price}")
            else:
                response_messages.append(f"❌ Unable to find stock ticker for **{name}**.")

        return "\n\n".join(response_messages)
        
    # ✅ Otherwise, proceed with normal response retrieval
    context_docs = query_chromadb(query)
    if not context_docs:
        return "❌ No relevant documents found in ChromaDB."

    context = "\n".join([f"- {doc}" for doc in context_docs])[:1024]

    # ✅ Maintain Chat History for Context
    chat_context = [{"role": "system", "content": context}]  # Start with retrieved docs
    chat_context.extend(st.session_state.chat_history)  # Add previous messages
    chat_context.append({"role": "user", "content": query})  # Add latest query

    # Mistral API Call
    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
        json={
            "model": "open-mistral-7b",
            "messages": chat_context,
            "max_tokens": 200,
            "temperature": 0.3,
            "top_p": 1,
            "stream": False,
        },
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.status_code} - {response.json()}"

# ✅ Chat Input Bar with Voice Option
col1, col2 = st.columns([8, 1])
with col1:
    user_query = st.text_input(
        "Type your message:",
        value=st.session_state.user_query,
        key=str(len(st.session_state.chat_history))  # Dynamic key to clear input field
    )

with col2:
    use_voice = st.button("🎙️ Speak")

# ✅ If Voice Button is Clicked, Convert Speech to Text & Append
if use_voice:
    voice_text = transcribe_audio()
    if voice_text:
        st.session_state.user_query += " " + voice_text  # Append to text bar
        st.rerun()  # Update UI dynamically
# ✅ Function: Convert Text to Speech (Using gTTS)
def speak_text(text):
    tts = gTTS(text=text, lang="en")
    audio_bytes = BytesIO()
    tts.save(audio_bytes)
    return audio_bytes.getvalue()
    
# ✅ Get Answer Button
if st.button("🔍 Get Answer"):
    if user_query.strip():  # Ensure non-empty query
        st.session_state.user_query = user_query  # Store query
        st.write("🔄 **Processing your request...**")
        response = generate_response(user_query)

        # ✅ Append conversation to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

        '''# ✅ Convert AI response to speech using gTTS
        tts = gTTS(text=response, lang="en")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        # ✅ Check if file exists before playing
        if os.path.exists(temp_file.name):
            st.audio(temp_file.name, format="audio/mp3")
        else:
            st.error("❌ Error: Audio file not found. Please try again.")

        # ✅ Display Audio Player in UI
        st.audio(temp_file.name, format="audio/mp3")'''
        st.write("### 📝 Chat History")
        for msg in st.session_state.chat_history:
            role = "👤 User" if msg["role"] == "user" else "🤖 AI"
            st.write(f"**{role}:** {msg['content']}")

        # ✅ Play Audio Response
        #st.audio(speak_text(response), format="audio/mp3")
    else:
        st.warning("⚠️ Please enter a question.")
        # ✅ Clear input field after submission
    st.session_state.user_query = ""  
    #st.rerun()  # Refresh UI dynamically

# ✅ Sidebar Info
st.sidebar.subheader("ℹ️ Info")
st.sidebar.write("This **Finance RAG AI** retrieves finance documents from ChromaDB and uses **Mistral-7B** for answers.")
st.sidebar.write("💡 **Now supports live stock price fetching via Yahoo Finance!** 📈")


