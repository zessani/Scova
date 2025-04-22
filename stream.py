# stream.py
# Simplified version that only calls backend API

import streamlit as st
import requests
import os
from datetime import datetime

# Configuration
BACKEND_URL = "http://127.0.0.1:8000" # Backend API URL

# Set page config
st.set_page_config(
    page_title="CryptoAnalyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# App title and description
st.title("CryptoAnalyst")
st.markdown("Advanced Crypto Market Analysis")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I'm your crypto analysis assistant. I can help you understand market trends, analyze specific cryptocurrencies, and provide insights about the blockchain ecosystem. How can I assist you today?"}
    ]

if "current_symbol" not in st.session_state:
    st.session_state.current_symbol = None

# Function to detect crypto symbol in text
def detect_crypto_symbol(text):
    crypto_patterns = {
        'bitcoin': 'BTC', 
        'ethereum': 'ETH', 
        'solana': 'SOL',
        'cardano': 'ADA',
        'ripple': 'XRP',
        'polkadot': 'DOT',
        'dogecoin': 'DOGE'
    }
    
    text_upper = text.upper()
    text_lower = text.lower()
    
    for name, symbol in crypto_patterns.items():
        if symbol in text_upper or name in text_lower:
            return symbol
    
    return None

# API Functions
def api_analyze_crypto(symbol):
    """Call backend API to analyze a cryptocurrency"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/analyze/{symbol}", timeout=60)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def api_follow_up(symbol, question):
    """Call backend API to handle a follow-up question"""
    try:
        payload = {
            "symbol": symbol,
            "question": question
        }
        response = requests.post(f"{BACKEND_URL}/api/followup", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about crypto markets, analysis, or trends..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Process message and generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.write("Thinking...")
        
        # Detect cryptocurrency in the message
        crypto_symbol = detect_crypto_symbol(prompt)
        
        try:
            # Case 1: Message contains a crypto symbol - do a new analysis
            if crypto_symbol:
                message_placeholder.write(f"Analyzing {crypto_symbol}...")
                st.session_state.current_symbol = crypto_symbol
                
                # Get analysis from API
                api_result = api_analyze_crypto(crypto_symbol)
                
                if "error" in api_result:
                    response = f"I encountered an error analyzing {crypto_symbol}: {api_result['error']}"
                else:
                    response = api_result["combined_analysis"]
            
            # Case 2: Follow-up question about current crypto
            elif st.session_state.current_symbol:
                symbol = st.session_state.current_symbol
                
                # Get answer from API
                api_result = api_follow_up(symbol, prompt)
                
                if "error" in api_result:
                    response = f"I encountered an error answering your question: {api_result['error']}"
                else:
                    response = api_result["response"]
            
            # Case 3: No crypto context
            else:
                response = "I'm not sure which cryptocurrency you're asking about. Could you mention a specific crypto symbol like BTC, ETH, or SOL?"
                
            # Update placeholder with final response
            message_placeholder.write(response)
            
            # Add response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            error_message = f"I encountered an error: {str(e)}"
            message_placeholder.write(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Add suggestion buttons for first-time users
if len(st.session_state.messages) <= 1:
    st.write("Try asking:")
    col1, col2 = st.columns(2)
    
    if col1.button("Analyze Bitcoin's recent price action"):
        st.session_state.messages.append({"role": "user", "content": "Analyze Bitcoin's recent price action"})
        st.rerun()
        
    if col2.button("Explain Ethereum's transition to proof-of-stake"):
        st.session_state.messages.append({"role": "user", "content": "Explain Ethereum's transition to proof-of-stake"})
        st.rerun()
        
    col3, col4 = st.columns(2)
    
    if col3.button("What are the top DeFi protocols right now?"):
        st.session_state.messages.append({"role": "user", "content": "What are the top DeFi protocols right now?"})
        st.rerun()
        
    if col4.button("Give me a market sentiment analysis"):
        st.session_state.messages.append({"role": "user", "content": "Give me a market sentiment analysis"})
        st.rerun()

# Footer
st.markdown("---")
st.caption("All market analysis is for informational purposes only")