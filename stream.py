# stream.py
import streamlit as st
import requests
import re

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
CRYPTO_SYMBOLS = {
    'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL', 'cardano': 'ADA',
    'ripple': 'XRP', 'polkadot': 'DOT', 'dogecoin': 'DOGE', 'chainlink': 'LINK',
    'avalanche': 'AVAX', 'polygon': 'MATIC'
}

# Page setup
st.set_page_config(
    page_title="CoinSight",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Global styles */
    .main { background-color: #f8f9fa !important; color: #212529; font-family: 'SF Pro Display', -apple-system, sans-serif; }
    .stApp { background-color: #f8f9fa !important; }
    
    /* Header */
    .header-container { padding: 1rem 0; border-bottom: 1px solid #eaeaea; margin-bottom: 2rem; }
    .product-name { font-size: 1.5rem; font-weight: 600; color: #333; }
    
    /* Chat container */
    .chat-container { max-width: 800px; margin: 0 auto; padding: 1rem; background-color: white; 
                     border-radius: 12px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05); }
    
    /* Sentiment meter */
    .sentiment-container { display: flex; align-items: center; margin-bottom: 1.5rem; 
                          padding-bottom: 1rem; border-bottom: 1px solid #f0f0f0; }
    .sentiment-label { font-size: 0.9rem; font-weight: 500; color: #666; margin-right: 1rem; }
    .sources-label { font-size: 0.9rem; font-weight: 500; color: #666; margin-left: auto; margin-right: 0.5rem; }
    .sources-count { display: inline-block; background-color: #f0f0f0; color: #333; 
                    font-size: 0.9rem; font-weight: 500; padding: 0.1rem 0.5rem; border-radius: 4px; }
    
    /* Sentiment meter visualization */
    .sentiment-track { height: 8px; background-color: #f0f0f0; border-radius: 4px; 
                      width: 150px; overflow: hidden; position: relative; }
    .sentiment-value { height: 100%; background: linear-gradient(90deg, #ff4d4d 0%, #ffe066 50%, #66bf6a 100%); width: 100%; }
    .sentiment-indicator { position: absolute; height: 100%; width: 3px; background-color: white; 
                          top: 0; border-radius: 1px; box-shadow: 0 0 3px rgba(0, 0, 0, 0.3); }
    
    /* Messages */
    .message { margin-bottom: 1.5rem; position: relative; }
    .message-icon { position: absolute; top: 0; left: 0; width: 24px; height: 24px; 
                   display: flex; align-items: center; justify-content: center; 
                   background-color: #f0f0f0; border-radius: 4px; font-size: 0.8rem; color: #666; }
    .message-content { margin-left: 2rem; font-size: 1rem; line-height: 1.5; color: #333; }
    
    /* Sources */
    .sources-container { margin-top: 0.5rem; font-size: 0.85rem; }
    .source-link { color: #1E88E5; text-decoration: underline; margin-right: 0.5rem; }
    
    /* Input area */
    .input-area { display: flex; margin-top: 2rem; border-radius: 8px; 
                 box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); overflow: hidden; }
    .stTextInput > div > div > input { background-color: white !important; color: #333 !important; 
                                      font-size: 1rem !important; border: none !important; 
                                      padding: 0.75rem 1rem !important; border-radius: 8px 0 0 8px !important; }
    .send-button { background-color: #daa520 !important; color: white !important; border: none !important; 
                  border-radius: 0 8px 8px 0 !important; padding: 0 1.5rem !important; 
                  font-weight: 500 !important; height: 100% !important; }
    
    /* Example buttons */
    .example-button { background-color: #f8f9fa !important; color: #666 !important; 
                     border: 1px solid #ddd !important; border-radius: 999px !important; 
                     padding: 0.5rem 1rem !important; font-size: 0.9rem !important; 
                     font-weight: 400 !important; margin-right: 0.5rem !important; 
                     margin-bottom: 0.5rem !important; transition: all 0.2s ease !important; }
    .example-button:hover { background-color: #f0f0f0 !important; border-color: #ccc !important; }
    
    /* Disclaimer */
    .disclaimer { font-size: 0.8rem; color: #999; text-align: center; margin-top: 2rem; }
    
    /* Hide unnecessary Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hello, I'm your crypto analysis assistant. I can help you understand market trends, analyze specific cryptocurrencies, and provide insights about the blockchain ecosystem. How can I assist you today?",
            "sentiment": 0.5,
            "sources": [],
            "sources_count": 0
        }
    ]
if "current_symbol" not in st.session_state:
    st.session_state.current_symbol = None
if "analyzed_symbols" not in st.session_state:
    st.session_state.analyzed_symbols = []
if "process_new_message" not in st.session_state:
    st.session_state.process_new_message = False

# API Functions
def api_analyze_crypto(symbol):
    try:
        response = requests.get(f"{BACKEND_URL}/api/analyze/{symbol}", timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def api_follow_up(symbol, question):
    try:
        payload = {"symbol": symbol, "question": question}
        response = requests.post(f"{BACKEND_URL}/api/followup", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def api_predict_price(symbol, timeframe):
    try:
        payload = {"symbol": symbol, "timeframe": timeframe}
        response = requests.post(f"{BACKEND_URL}/api/predict", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def api_strategy(symbol, goal):
    try:
        payload = {"symbol": symbol, "goal": goal}
        response = requests.post(f"{BACKEND_URL}/api/strategy", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def detect_crypto_symbol(text):
    text_upper = text.upper()
    text_lower = text.lower()
    
    for name, symbol in CRYPTO_SYMBOLS.items():
        if symbol in text_upper or name in text_lower:
            return symbol
    
    return None

# UI Layout
st.markdown('<div class="header-container"><span class="product-name">CoinSight</span></div>', unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display sentiment meter for the most recent assistant message
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    latest_message = st.session_state.messages[-1]
    sentiment_value = latest_message.get("sentiment", 0.5)
    sources_count = latest_message.get("sources_count", 0)
    
    st.markdown(f"""
    <div class="sentiment-container">
        <span class="sentiment-label">Market Sentiment</span>
        <div class="sentiment-track">
            <div class="sentiment-value"></div>
            <div class="sentiment-indicator" style="left: {sentiment_value * 100}%;"></div>
        </div>
        <span class="sources-label">Sources</span>
        <span class="sources-count">{sources_count}</span>
    </div>
    """, unsafe_allow_html=True)

# Display messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    sources = message.get("sources", [])
    
    icon = "👤" if role == "user" else "🤖"
    
    # Create source links HTML if there are sources
    sources_html = ""
    if role == "assistant" and sources:
        sources_html = '<div class="sources-container"><strong>Sources:</strong> '
        for source in sources:
            name = source.get("name", "")
            url = source.get("url", "")
            if url:
                sources_html += f'<a href="{url}" target="_blank" class="source-link">{name}</a>'
            else:
                sources_html += f'<span class="source-link">{name}</span>'
        sources_html += '</div>'
    
    st.markdown(f"""
    <div class="message">
        <div class="message-icon">{icon}</div>
        <div class="message-content">
            {content}
            {sources_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display example buttons for first-time users
if len(st.session_state.messages) <= 1:
    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("What's happening with Ethereum?", key="example1", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "What's happening with Ethereum?",
            })
            st.session_state.process_new_message = True
            st.rerun()
    
    with col2:
        if st.button("When should I sell my BTC?", key="example2", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "When should I sell my BTC?",
            })
            st.session_state.process_new_message = True
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-area">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    prompt = st.text_input("Ask a question", placeholder="Ask about crypto markets, analysis, or trends...", 
                          label_visibility="collapsed", key="chat_input")
with col2:
    send_button = st.button("→", key="send_button", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Disclaimer
st.markdown('<div class="disclaimer">All market analysis is for informational purposes only</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # Close chat container

# Message handling logic
if send_button and prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.process_new_message = True
    st.rerun()

if st.session_state.process_new_message and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]
    
    with st.spinner("Analyzing..."):
        crypto_symbol = detect_crypto_symbol(prompt)
        if not crypto_symbol and st.session_state.current_symbol:
            crypto_symbol = st.session_state.current_symbol
        
        if crypto_symbol:
            st.session_state.current_symbol = crypto_symbol
            
            # Determine request type based on query
            if "predict" in prompt.lower() or "forecast" in prompt.lower():
                timeframe = "month"  # Default
                if "week" in prompt.lower():
                    timeframe = "week"
                elif "3 month" in prompt.lower() or "three month" in prompt.lower():
                    timeframe = "3months"
                
                api_result = api_predict_price(crypto_symbol, timeframe)
                if "error" in api_result:
                    response_data = {
                        "content": f"I encountered an error: {api_result['error']}",
                        "sentiment": 0.5,
                        "sources": [],
                        "sources_count": 0
                    }
                else:
                    response_data = {
                        "content": api_result["prediction"],
                        "sentiment": api_result.get("sentiment_score", 50) / 100,  # Convert 0-100 to 0-1
                        "sources": api_result.get("sources", []),
                        "sources_count": api_result.get("sources_count", 0)
                    }
            
            elif any(phrase in prompt.lower() for phrase in ["when should i", "strategy", "timing", "best time", "maximize"]):
                api_result = api_strategy(crypto_symbol, prompt)
                if "error" in api_result:
                    response_data = {
                        "content": f"I encountered an error: {api_result['error']}",
                        "sentiment": 0.5,
                        "sources": [],
                        "sources_count": 0
                    }
                else:
                    response_data = {
                        "content": api_result["strategy"],
                        "sentiment": api_result.get("sentiment_score", 50) / 100,
                        "sources": api_result.get("sources", []),
                        "sources_count": api_result.get("sources_count", 0)
                    }
            
            else:
                # Get base analysis if needed
                if crypto_symbol not in st.session_state.analyzed_symbols:
                    api_analyze_crypto(crypto_symbol)
                    st.session_state.analyzed_symbols.append(crypto_symbol)
                
                # Handle follow-up question
                api_result = api_follow_up(crypto_symbol, prompt)
                if "error" in api_result:
                    response_data = {
                        "content": f"I encountered an error: {api_result['error']}",
                        "sentiment": 0.5,
                        "sources": [],
                        "sources_count": 0
                    }
                else:
                    response_data = {
                        "content": api_result["response"],
                        "sentiment": api_result.get("sentiment_score", 50) / 100,
                        "sources": api_result.get("sources", []),
                        "sources_count": api_result.get("sources_count", 0)
                    }
        else:
            response_data = {
                "content": "I'm not sure which cryptocurrency you're asking about. Could you mention a specific crypto symbol like BTC, ETH, or SOL?",
                "sentiment": 0.5,
                "sources": [],
                "sources_count": 0
            }
        
        st.session_state.messages.append({"role": "assistant", **response_data})
        st.session_state.process_new_message = False
        st.rerun()