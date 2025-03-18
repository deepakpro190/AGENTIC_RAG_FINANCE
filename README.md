
# **Finance RAG AI – Intelligent Financial Chatbot** 💰  

**Finance RAG AI** is a **Retrieval-Augmented Generation (RAG)-based financial chatbot** that leverages **Mistral-7B**, **FAISS** for vector search, and **Streamlit** for an interactive user interface. It provides financial insights, retrieves real-time stock prices, aggregates financial news, and supports **voice-based interaction**, offering a seamless financial analysis experience.  

---

## **🚀 Key Features**  

### 🔍 **Retrieval-Augmented Generation (RAG)**
- Uses **FAISS (Facebook AI Similarity Search)** for **efficient vector-based financial data retrieval**.  
- Enhances financial responses by integrating relevant information from stored documents.  

### 🤖 **Multi-Agent Financial Intelligence**  
- **Market Insights Agent:** Analyzes stock trends and market patterns.  
- **Stock Price Agent:** Fetches real-time stock prices from **Yahoo Finance**.  
- **News Aggregation Agent:** Retrieves and summarizes **latest financial news**.  
- **Query Analysis Agent:** Identifies user intent and routes queries to the appropriate agent.  

### 📈 **Real-Time Financial Data Analysis**  
- Extracts key financial metrics such as **P/E ratio, market capitalization, dividend yield, volatility (beta), moving averages**, and more.  
- Generates **stock performance comparisons** and **trend visualizations**.  

### 🎙️ **Voice-Enabled Chatbot**  
- Supports **speech-to-text** (voice input) and **text-to-speech (TTS)** for an **interactive, hands-free financial assistant**.  

### 📝 **Conversational Memory & Context Awareness**  
- Maintains **chat history** to ensure contextual, coherent financial discussions.  

### 🌐 **User-Friendly Web Interface**  
- Built with **Streamlit**, providing an intuitive and interactive user experience.  

---

## **📂 Project Structure**  

```
📦 Finance-RAG-AI  
│-- 📁 agents/  
│   ├── market_insights.py   # Analyzes stock market trends  
│   ├── news_aggregator.py   # Fetches latest financial news  
│   ├── query_analysis.py    # Determines query intent (e.g., stock price, news, insights)  
│   ├── stock_price.py       # Fetches real-time stock prices  
│  
│-- 📁 utils/  
│   ├── faiss_utils.py       # FAISS-based vector search for finance data  
│   ├── llm_utils.py         # Handles interaction with Mistral-7B LLM  
│   ├── plot_utils.py        # Generates stock trend visualizations  
│   ├── voice_utils.py       # Speech-to-text & text-to-speech processing  
│  
│-- 📄 app.py                # Main Streamlit application  
│-- 📄 requirements.txt      # Python dependencies  
│-- 📄 README.md             # Project documentation  
│-- 📄 .streamlit/secrets.toml # Secure storage for API keys  
```

---

## **🔧 Installation & Setup**  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/your-username/finance-rag-ai.git  
cd finance-rag-ai
```

### **2️⃣ Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **3️⃣ Configure API Keys**  
Create a `.streamlit/secrets.toml` file and add your **Mistral API key**:  
```
[MISTRAL]
MISTRAL_API_KEY = "your-api-key-here"
```

### **4️⃣ Run the Application**  
```bash
streamlit run app.py
```

---

## **🌐 Deployment on Streamlit Cloud**  

🚀 Deploy this app on **Streamlit Cloud** using the following link:  
🔗 **[https://agenticragfinance-uwcwzh6zxkhto9yzod5sed.streamlit.app/
](#)** 

---

## **🤖 Is This an Agentic System?**  

Yes! **Finance RAG AI is an agentic chatbot**.  
It follows an **autonomous multi-agent architecture**, where **specialized agents** (market insights, stock prices, financial news aggregation, and query analysis) **collaborate** to deliver comprehensive and accurate financial responses.  

Each agent performs a distinct role, making the chatbot **modular, scalable, and efficient** in handling complex financial queries.  



## **🛠️ Technology Stack**  

- **LLM Model:** Mistral-7B (Advanced Open-Source LLM for finance Q&A)  
- **Vector Database:** FAISS (Fast Approximate Nearest Neighbor Search for financial data)  
- **Data Sources:** Yahoo Finance (Stock prices), Financial News APIs  
- **Speech Processing:** Google Speech-to-Text, pyttsx3 for TTS  
- **Frameworks & Libraries:** Streamlit, FAISS, Requests, Matplotlib, yfinance  


🚀 **Empowering Financial Conversations with AI!** 💰
