'''import streamlit as st
import yfinance as yf
from agents.query_analysis import analyze_query_with_llm
from agents.stock_price import fetch_stock_price
from agents.market_insights import analyze_stock_trends
from agents.news_aggregator import fetch_financial_news
from utils.faiss_utils import query_faiss

from utils.voice_utils import transcribe_audio, speak_text
from utils.plot_utils import plot_stock_trend
import requests



MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

# ✅ Initialize session state for chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores full chat history

if "user_query" not in st.session_state:
    st.session_state.user_query = ""  # Stores ongoing user query

def generate_response(user_query):
    """
    Generates response using LLM, incorporating relevant documents from ChromaDB.
    """
    try:
        # ✅ Step 1: Retrieve documents from ChromaDB
        docs = query_faiss(user_query)


        if not docs:
            context = "No relevant documents found in ChromaDB."
        else:
            context = "\n".join([f"- {doc}" for doc in docs])[:1024]  # Limit to 1024 tokens

        # ✅ Step 2: Maintain Chat Context
        chat_context = [
            {"role": "system", "content": f"You are a finance AI assistant. Use the following information to assist the user:\n\n{context}"},
            {"role": "user", "content": user_query}
        ]

        # ✅ Step 3: Add previous chat history (if available)
        chat_context.extend(st.session_state.chat_history)

        # ✅ Step 4: Call Mistral LLM
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

        # ✅ Step 5: Extract and return LLM response
        if response.status_code == 200:
            llm_response = response.json()["choices"][0]["message"]["content"]
            return llm_response
        else:
            return f"❌ Error: {response.status_code} - {response.json()}"

    except Exception as e:
        return f"❌ Error in response generation: {str(e)}"


def extract_stock_details(companies):
    """
    Extracts multiple financial details for stock comparison.
    :param companies: List of dicts [{"name": "Tesla", "ticker": "TSLA"}]
    :return: Dict of stock details
    """
    stock_data = {}

    for company in companies:
        ticker = company["ticker"]
        stock = yf.Ticker(ticker)
        history = stock.history(period="6mo")

        if history.empty:
            continue  # Skip if no data

        latest_price = history["Close"].iloc[-1]
        price_6mo_ago = history["Close"].iloc[0]
        percent_change = ((latest_price - price_6mo_ago) / price_6mo_ago) * 100

        # ✅ Extract more financial details
        info = stock.info
        market_cap = info.get("marketCap", "N/A")
        pe_ratio = info.get("trailingPE", "N/A")
        dividend_yield = info.get("dividendYield", "N/A")
        beta = info.get("beta", "N/A")
        avg_volume = info.get("averageVolume", "N/A")
        moving_avg_50 = info.get("fiftyDayAverage", "N/A")
        moving_avg_200 = info.get("twoHundredDayAverage", "N/A")

        # ✅ Store extracted data
        stock_data[ticker] = {
            "name": company["name"],
            "latest_price": latest_price,
            "percent_change": percent_change,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "beta": beta,
            "avg_volume": avg_volume,
            "moving_avg_50": moving_avg_50,
            "moving_avg_200": moving_avg_200,
        }

    return stock_data
def generate_professional_stock_analysis(stock_data):
    """
    Uses LLM to generate a professional comparison of stocks.
    :param stock_data: Extracted financial data
    :return: String summary from LLM
    """
    if not stock_data:
        return "❌ No stock data available for comparison."

    # ✅ Convert extracted stock data into a structured prompt
    analysis_prompt = "Compare the following stocks based on key financial metrics:\n\n"

    for ticker, data in stock_data.items():
        analysis_prompt += (
            f"**{data['name']} ({ticker})**\n"
            f"- **Current Price:** ${data['latest_price']:.2f}\n"
            f"- **6-Month Change:** {data['percent_change']:.2f}%\n"
            f"- **Market Cap:** {data['market_cap']}\n"
            f"- **P/E Ratio:** {data['pe_ratio']}\n"
            f"- **Dividend Yield:** {data['dividend_yield']}\n"
            f"- **Beta (Volatility):** {data['beta']}\n"
            f"- **Avg. Daily Volume:** {data['avg_volume']}\n"
            f"- **50-Day Moving Avg:** {data['moving_avg_50']}\n"
            f"- **200-Day Moving Avg:** {data['moving_avg_200']}\n\n"
        )

    analysis_prompt += "Provide a detailed financial analysis and comparison of these stocks."

    # ✅ Call LLM to generate a professional analysis
    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
        json={
            "model": "open-mistral-7b",
            "messages": [
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": analysis_prompt},
            ],
            "max_tokens": 400,
            "temperature": 0.3,
            "top_p": 1,
            "stream": False,
        },
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error fetching analysis: {response.status_code} - {response.json()}"

st.set_page_config(page_title="💰 Finance RAG AI", layout="wide")
st.title("💰 Finance RAG AI - Chat Mode")

# ✅ Display chat history
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.write(chat["bot"])

        
col1, col2 = st.columns([8, 1])

with col1:
    user_query = st.text_input(
        "Type your message:",
        value=st.session_state.user_query,
        key=str(len(st.session_state.chat_history))  # Dynamic key to clear input field
    )

with col2:
    use_voice = st.button("🎙️ Speak")

# ✅ If Voice Button is Clicked, Convert Speech to Text
if use_voice:
    voice_text = transcribe_audio()
    if voice_text:
        st.session_state.user_query += " " + voice_text  # Append to text bar
        st.rerun()

if st.button("🔍 Get Answer"):
    if user_query.strip():
        st.session_state.user_query = user_query  # Store query
        st.write("🔄 **Processing...**")
        llm_result = analyze_query_with_llm(user_query)

        if llm_result["query_type"] == "stock_price":
            response = "\n\n".join([fetch_stock_price(c["ticker"]) for c in llm_result["companies"]])

        elif llm_result["query_type"] == "compare":
            # ✅ Generate stock trend plot
            fig = analyze_stock_trends(llm_result["companies"])  
            st.pyplot(fig)  # Display the chart
        
            # ✅ Extract financial data for detailed analysis
            stock_details = extract_stock_details(llm_result["companies"])
        
            # ✅ Generate LLM-enhanced summary using the extracted data
            theoretical_analysis = generate_professional_stock_analysis(stock_details)
        
            # ✅ Display insights
            st.write("### 📊 Stock Performance & Financial Insights")
            st.write(theoretical_analysis)
        
            # ✅ Final response
            response = theoretical_analysis + "\n\n📊 See the stock performance comparison above."




        elif llm_result["query_type"] == "news":
            response = fetch_financial_news()

        else:
            response = generate_response(user_query)

        # ✅ Add to chat history
        st.session_state.chat_history.append({"user": user_query, "bot": response})
        st.write(response)
         # ✅ Clear input field
        st.session_state.user_query = ""
        # ✅ Convert response to speech
        # ✅ Play the audio response
        audio_file = speak_text(response)
        if isinstance(audio_file, str) and audio_file.endswith(".mp3"):
            st.audio(audio_file, format="audio/mp3")
        else:
            st.error(audio_file)  # Show error message if TTS fails
'''
import streamlit as st
import yfinance as yf
import requests
from agents.query_analysis import analyze_query_with_llm
from agents.stock_price import fetch_stock_price
from agents.market_insights import analyze_stock_trends
from agents.news_aggregator import fetch_financial_news
from utils.faiss_utils import query_faiss
from utils.plot_utils import plot_stock_trend
from utils.voice_utils import speak_text

# ✅ Load API Key from Streamlit Secrets
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

# ✅ Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

# ✅ Function to generate LLM response
def generate_response(user_query):
    try:
        docs = query_faiss(user_query)
        context = "\n".join([f"- {doc}" for doc in docs])[:1024] if docs else "No relevant documents found."
        
        chat_context = [
            {"role": "system", "content": f"You are a finance AI assistant. Use this information:\n\n{context}"},
            {"role": "user", "content": user_query}
        ]
        chat_context.extend(st.session_state.chat_history)

        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={
                "model": "open-mistral-7b",
                "messages": chat_context,
                "max_tokens": 200,
                "temperature": 0.3,
                "top_p": 1,
            },
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"❌ Error: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"❌ Error in response generation: {str(e)}"

# ✅ Set Streamlit page config
st.set_page_config(page_title="💰 Finance RAG AI", layout="wide")
st.title("💰 Finance RAG AI - Chat Mode")

# ✅ Display chat history
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.write(chat["bot"])

# ✅ JavaScript Speech-to-Text Component
st.components.v1.html(
    """
    <script>
        function startListening() {
            var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.start();

            recognition.onresult = function(event) {
                var speechText = event.results[0][0].transcript;
                document.getElementById("output").value = speechText;
                document.getElementById("hiddenInput").value = speechText;
                document.getElementById("submit").click();
            };

            recognition.onerror = function(event) {
                alert("Speech recognition error: " + event.error);
            };
        }
    </script>

    <button onclick="startListening()">🎙️ Speak</button>
    <input type="text" id="output" readonly />
    <form action="" method="get">
        <input type="hidden" id="hiddenInput" name="voice_input" />
        <input type="submit" id="submit" style="display: none;" />
    </form>
    """,
    height=150
)

# ✅ Get voice input from URL parameters
query_params = st.experimental_get_query_params()
voice_text = query_params.get("voice_input", [""])[0]

# ✅ Update session state with voice input
if voice_text:
    st.session_state.user_query = voice_text
    st.experimental_rerun()

# ✅ User Input
user_query = st.text_input("Type your message:", value=st.session_state.user_query, key=str(len(st.session_state.chat_history)))

if st.button("🔍 Get Answer"):
    if user_query.strip():
        st.session_state.user_query = user_query
        st.write("🔄 **Processing...**")
        
        llm_result = analyze_query_with_llm(user_query)
        
        if llm_result["query_type"] == "stock_price":
            response = "\n\n".join([fetch_stock_price(c["ticker"]) for c in llm_result["companies"]])
        elif llm_result["query_type"] == "compare":
            fig = analyze_stock_trends(llm_result["companies"])  
            st.pyplot(fig)
            stock_details = extract_stock_details(llm_result["companies"])
            theoretical_analysis = generate_professional_stock_analysis(stock_details)
            st.write("### 📊 Stock Performance & Financial Insights")
            st.write(theoretical_analysis)
            response = theoretical_analysis + "\n\n📊 See the stock performance comparison above."
        elif llm_result["query_type"] == "news":
            response = fetch_financial_news()
        else:
            response = generate_response(user_query)

        # ✅ Add to chat history and display response
        st.session_state.chat_history.append({"user": user_query, "bot": response})
        st.write(response)

        # ✅ Convert response to speech
        audio_file = speak_text(response)
        if isinstance(audio_file, str) and audio_file.endswith(".mp3"):
            st.audio(audio_file, format="audio/mp3")
        else:
            st.error(audio_file)

        # ✅ Clear input field
        st.session_state.user_query = ""

st.sidebar.subheader("ℹ️ Info")
st.sidebar.write("This **Finance RAG AI** retrieves finance documents from FAISS and uses **Mistral-7B** for answers.")

        #st.audio(speak_text(response), format="audio/mp3")

st.sidebar.subheader("ℹ️ Info")
st.sidebar.write("This **Finance RAG AI** retrieves finance documents from FAISS and uses **Mistral-7B** for answers.")
