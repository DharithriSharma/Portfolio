import streamlit as st
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import ta

from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StreamlitCallbackHandler

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

st.title("📈 AI StockBot: Robust Analysis System")

# ========== Sidebar Configuration ==========
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Groq API Key:", type="password")
stock_symbol = st.sidebar.text_input("Stock Symbol (e.g., INFY.NS):", "INFY.NS")
start_date = st.sidebar.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=365))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# ========== Enhanced Data Handling ==========
def fetch_stock_data():
    try:
        data = yf.download(stock_symbol, start=start_date, end=end_date)
        if data.empty:
            return None, "No data found for this symbol"

        close_series = data['Close'].squeeze()
        data['SMA_20'] = close_series.rolling(20).mean()
        data['RSI'] = ta.momentum.RSIIndicator(close_series).rsi()
        clean_data = data.dropna()

        if len(clean_data) == 0:
            return None, "Not enough data after cleaning"

        return clean_data, None

    except Exception as e:
        return None, f"Data error: {str(e)}"

def plot_stock_data(data):
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data.index, data['Close'], label='Price')
        ax.plot(data.index, data['SMA_20'], label='20-day SMA', linestyle='--')
        ax.set_title(f"{stock_symbol} Analysis")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Plotting error: {str(e)}")

# ========== AI Tools ==========
def technical_analysis(query: str) -> str:
    data, error = fetch_stock_data()
    if error:
        return error

    try:
        last = data.iloc[-1]
        close_price = float(last['Close'])
        sma_20 = float(last['SMA_20'])
        rsi = float(last['RSI'])
        volume = int(last['Volume'])

        return (
            f"📊 **Latest Technical Data**:\n"
            f"- Close: ₹{close_price:.2f}\n"
            f"- SMA 20: ₹{sma_20:.2f}\n"
            f"- RSI: {rsi:.1f}\n"
            f"- Volume: {volume:,}"
        )
    except Exception as e:
        return f"Technical analysis failed: {str(e)}"

def fundamental_analysis(query: str) -> str:
    try:
        ticker = yf.Ticker(stock_symbol)
        info = ticker.info
        return (
            f"📊 **Fundamental Data**:\n"
            f"- Name: {info.get('longName', 'N/A')}\n"
            f"- Sector: {info.get('sector', 'N/A')}\n"
            f"- Market Cap: ₹{info.get('marketCap', 'N/A'):,}\n"
            f"- PE Ratio: {info.get('trailingPE', 'N/A')}"
        )
    except Exception as e:
        return f"Fundamental analysis failed: {str(e)}"

# ========== Agent Setup ==========
tools = [
    Tool(
        name="Technical",
        func=technical_analysis,
        description="For price trends and technical indicators"
    ),
    Tool(
        name="Fundamental",
        func=fundamental_analysis,
        description="For company financials and ratios"
    )
]

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

if api_key:
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="Llama3-8b-8192",
        temperature=0.3
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=5
    )

# ========== Main Interface ==========
if prompt := st.chat_input("Ask about the stock (e.g., 'Analyze INFY'):"):
    if not api_key:
        st.error("❌ Missing Groq API Key")
        st.stop()

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            st_cb = StreamlitCallbackHandler(st.container())
            data, _ = fetch_stock_data()

            if data is not None:
                plot_stock_data(data)

            raw_response = agent.run(prompt, callbacks=[st_cb])

            # Remove repeated lines
            filtered_response = "\n".join(dict.fromkeys(raw_response.splitlines()))

            st.write(filtered_response)

            if not st.session_state.history or st.session_state.history[-1]['response'] != filtered_response:
                st.session_state.history.append({
                    "symbol": stock_symbol,
                    "query": prompt,
                    "response": filtered_response
                })

        except Exception as e:
            st.error(f"System error: {str(e)}")

# ========== History Panel ==========
st.sidebar.markdown("## Recent Queries")
for entry in st.session_state.history[-3:]:
    with st.sidebar.expander(f"{entry['symbol']}: {entry['query'][:15]}..."):
        st.write(f"**Query:** {entry['query']}")
        st.write(f"**Response:** {entry['response']}")

st.sidebar.markdown("---")
st.sidebar.caption("Financial data provided by Yahoo Finance")
