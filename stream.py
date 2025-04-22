# stream.py

import streamlit as st
import os
import asyncio
import re
from datetime import datetime
from dotenv import load_dotenv
from backend.app.agents.data_agent import DataAgent
from backend.app.agents.sentiment_agent import SentimentAgent
from openai import OpenAI

# Load environment variables
load_dotenv()

# Synchronous wrappers for async functions
def analyze_crypto_sync(symbol):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(data_agent.analyze_crypto(symbol))
    loop.close()
    return result

def analyze_sentiment_sync(symbol):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(sentiment_agent.get_news_data(symbol))
    loop.close()
    return result

# Helper functions to extract sources and sentiment
def extract_sources_from_analysis(market_analysis, sentiment_analysis):
    """Extract specific sources mentioned in the analyses"""
    sources = []
    
    # Combined text to search through
    combined_text = f"{market_analysis}\n{sentiment_analysis}"
    
    # Extract quotes which often indicate source material
    quote_patterns = [r'"([^"]*)"', r"'([^']*)'", r'"([^"]*)"']
    quotes = []
    for pattern in quote_patterns:
        quotes.extend(re.findall(pattern, combined_text))
    
    # Look for specific source mentions
    source_patterns = [
        (r'according to ([^,.]{3,50})', 'Analysis Mention'),
        (r'reported by ([^,.]{3,50})', 'News Report'),
        (r'from ([^,.]{3,50})', 'Source'),
        (r'([^,.]{3,50}) (reports|reported|states|stated)', 'Report'),
        (r'data from ([^,.]{3,50})', 'Data Source'),
        (r'([^,.]{3,40}) analytics', 'Analytics'),
        (r'on ([^,.]*twitter|x)', 'Social Media'),
        (r'tweet from ([^,.]*)', 'Tweet'),
        (r'article by ([^,.]*)', 'Article')
    ]
    
    # Extract sources
    for pattern, source_type in source_patterns:
        matches = re.findall(pattern, combined_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            
            # Find surrounding context
            context = find_context(combined_text, match)
            
            sources.append({
                "Source": match.strip(),
                "Type": source_type,
                "Content": context,
                "Reliability": "Medium"
            })
    
    # Process quotes
    for quote in quotes:
        if len(quote) > 20:  # Filter out short quotes
            context = find_context(combined_text, quote)
            attribution = extract_attribution(context, quote)
            
            sources.append({
                "Source": attribution if attribution else "Quoted Content",
                "Type": "Quote",
                "Content": quote,
                "Reliability": "Medium"
            })
    
    # Add standard sources that are always used
    sources.extend([
        {
            "Source": "Polygon.io",
            "Type": "Market Data",
            "Content": "Price and volume data from Polygon API",
            "Reliability": "High",
            "Link": "https://polygon.io/"
        },
        {
            "Source": "News API",
            "Type": "News Aggregator",
            "Content": "Recent news articles from various publishers",
            "Reliability": "Medium",
            "Link": "https://newsapi.org/"
        },
        {
            "Source": "OpenAI API",
            "Type": "Analysis Engine",
            "Content": "Analysis of market data and sentiment",
            "Reliability": "Medium",
            "Link": "https://openai.com/"
        }
    ])
    
    # Remove duplicates
    unique_sources = []
    seen = set()
    
    for source in sources:
        source_key = (source["Source"], source["Content"][:50])
        if source_key not in seen:
            seen.add(source_key)
            unique_sources.append(source)
    
    return unique_sources

def find_context(text, phrase, window=100):
    """Find surrounding context of a phrase"""
    try:
        phrase = str(phrase).lower()
        text_lower = text.lower()
        
        start_idx = text_lower.find(phrase)
        if start_idx != -1:
            context_start = max(0, start_idx - window)
            context_end = min(len(text), start_idx + len(phrase) + window)
            return text[context_start:context_end].strip()
        return ""
    except:
        return ""

def extract_attribution(context, quote):
    """Try to extract who said the quote"""
    try:
        # Check for attribution patterns
        attribution_patterns = [
            r'(?:' + re.escape(quote) + r')\s*,?\s*(?:said|according to|noted by|by|from)\s+([^,.]{3,40})',
            r'(?:' + re.escape(quote) + r')\s*,?\s*([^,.]{3,40})\s+(?:said|reported|noted|stated)',
            r'(?:as|as per)\s+([^,.]{3,40})\s*,?\s*'
        ]
        
        for pattern in attribution_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    except:
        pass
    
    return None

def extract_sentiment_metrics(sentiment_text):
    """Extract sentiment metrics and mentions from analysis"""
    # Overall sentiment detection
    sentiment_indicators = {
        "highly bullish": 90, "bullish": 75, "positive": 70,
        "neutral": 50, "mixed": 50,
        "negative": 30, "bearish": 25, "highly bearish": 10
    }
    
    # Set default overall sentiment
    overall = 50
    sentiment_description = "Neutral"
    
    # Check for overall sentiment in the text
    text_lower = sentiment_text.lower()
    for indicator, value in sentiment_indicators.items():
        if indicator in text_lower[:200]:  # Check beginning of text
            overall = value
            sentiment_description = indicator.title()
            break
    
    # Find specific sentiment mentions
    sentiment_mentions = []
    
    # Extract specific sentiment statements
    sentiment_patterns = [
        r"(social media|twitter|reddit)\s+(?:sentiment|reaction)\s+(?:is|has been|appears)\s+([a-z]+)",
        r"(news articles|publications|press)\s+(?:are|have been|appear)\s+([a-z]+)",
        r"(trading volume|market volume)\s+(?:is|has been|appears)\s+([a-z]+)",
        r"(market volatility|price volatility)\s+(?:is|has been|appears)\s+([a-z]+)",
        r"(institutional interest|institutional investors)\s+(?:are|have been|appear)\s+([a-z]+)",
        r"sentiment (?:around|regarding|concerning)\s+([^\.,]+)\s+(?:is|has been|appears)\s+([a-z]+)"
    ]
    
    for pattern in sentiment_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if isinstance(match, tuple) and len(match) == 2:
                source, sentiment = match
                
                # Map sentiment words to values
                sentiment_value = 50  # Default neutral
                for indicator, value in sentiment_indicators.items():
                    if indicator in sentiment or sentiment in indicator:
                        sentiment_value = value
                        break
                
                # Add to mentions
                sentiment_mentions.append({
                    "Source": source.strip().title(),
                    "Sentiment": sentiment.strip(),
                    "Value": sentiment_value,
                    "Context": find_context(sentiment_text, source)
                })
    
    # Predefined categories for the chart
    categories = [
        "Social Media", "News Articles", "Trading Volume", 
        "Market Volatility", "Institutional Interest"
    ]
    
    # Map mentions to categories
    category_values = {}
    for mention in sentiment_mentions:
        source = mention["Source"]
        value = mention["Value"]
        
        # Match to predefined categories
        for category in categories:
            if category.lower() in source.lower():
                category_values[category] = value
                break
    
    # Fill in missing categories with default value
    for category in categories:
        if category not in category_values:
            # Use overall sentiment as default for missing categories
            category_values[category] = overall
    
    # Create trend arrows
    sentiment_data = []
    for category in categories:
        value = category_values[category]
        if value > 60:
            trend = "↑"
        elif value < 40:
            trend = "↓"
        else:
            trend = "→"
        
        sentiment_data.append({
            "Category": category,
            "Value": value,
            "Trend": trend
        })
    
    # Create metrics result
    metrics = {
        "overall": overall,
        "description": sentiment_description,
        "data": sentiment_data,
        "mentions": sentiment_mentions
    }
    
    return metrics

def get_news_data_sync(symbol, limit=10):
    """Get news data synchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(sentiment_agent.get_news_data(symbol, limit))
    loop.close()
    return result

# Initialize agents and OpenAI client
data_agent = DataAgent()
sentiment_agent = SentimentAgent()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
analysis_cache = {}

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

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I'm your crypto analysis assistant. I can help you understand market trends, analyze specific cryptocurrencies, and provide insights about the blockchain ecosystem. How can I assist you today?"}
    ]

# Function to detect crypto symbol
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
    
    # Check for symbol or name
    text_upper = text.upper()
    text_lower = text.lower()
    
    for name, symbol in crypto_patterns.items():
        if symbol in text_upper or name in text_lower:
            return symbol
    
    return None

# Display chat messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Show analysis buttons for assistant messages with crypto analysis
        if message["role"] == "assistant" and "current_symbol" in st.session_state:
            cols = st.columns(2)
            if cols[0].button("View Sources", key=f"sources_{idx}"):
                st.session_state.show_sources = True
                st.session_state.viewing_symbol = st.session_state.current_symbol
            if cols[1].button("Sentiment Analysis", key=f"sentiment_{idx}"):
                st.session_state.show_sentiment = True
                st.session_state.viewing_symbol = st.session_state.current_symbol

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
            if crypto_symbol:
                st.session_state.current_symbol = crypto_symbol
                message_placeholder.write(f"Analyzing {crypto_symbol}...")
                
                # Get analysis from backend using sync wrappers
                market_analysis = analyze_crypto_sync(crypto_symbol)
                sentiment_analysis = analyze_sentiment_sync(crypto_symbol)
                
                # Generate combined analysis
                completion = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""You are Cryptosys analyzing {crypto_symbol}. Here's the data:
                            
                            TECHNICAL ANALYSIS:
                            {market_analysis}
                            
                            SENTIMENT ANALYSIS:
                            {sentiment_analysis}
                            
                            Respond conversationally with:
                            1. Current price and trend
                            2. Key insights from both analyses
                            3. Where data agrees or conflicts
                            4. Overall assessment and recommendation
                            
                            Keep it concise."""
                        }
                    ]
                )
                
                response = completion.choices[0].message.content
                
                # Extract sources and sentiment metrics
                sources = extract_sources_from_analysis(market_analysis, sentiment_analysis)
                sentiment_metrics = extract_sentiment_metrics(sentiment_analysis)
                
                # Cache the analysis data
                analysis_cache[crypto_symbol] = {
                    "symbol": crypto_symbol,
                    "market_analysis": market_analysis,
                    "sentiment_analysis": sentiment_analysis,
                    "combined_analysis": response,
                    "sources": sources,
                    "sentiment_metrics": sentiment_metrics,
                    "news_data": get_news_data_sync(crypto_symbol)
                }
                
            elif "current_symbol" in st.session_state:
                # Handle follow-up question about current symbol
                symbol = st.session_state.current_symbol
                
                if symbol in analysis_cache:
                    cached = analysis_cache[symbol]
                    
                    completion = openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {
                                "role": "user",
                                "content": f"""You are Cryptosys. You previously analyzed {symbol} with this information:
                                
                                MARKET ANALYSIS:
                                {cached['market_analysis']}
                                
                                SENTIMENT ANALYSIS:
                                {cached['sentiment_analysis']}
                                
                                The user is asking: "{prompt}"
                                
                                Answer concisely based on your analysis."""
                            }
                        ]
                    )
                    
                    response = completion.choices[0].message.content
                else:
                    response = f"I don't have any analysis data for {symbol}. Would you like me to analyze it?"
            else:
                response = "I'm not sure which cryptocurrency you're asking about. Could you mention a specific crypto symbol like BTC, ETH, or SOL?"
                
            # Update placeholder with final response
            message_placeholder.write(response)
            
            # Add response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            message_placeholder.write(f"I encountered an error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"I encountered an error: {str(e)}"})

# Display sources modal
if "show_sources" in st.session_state and st.session_state.show_sources:
    with st.expander("Analysis Sources", expanded=True):
        if "viewing_symbol" in st.session_state:
            symbol = st.session_state.viewing_symbol
            st.subheader(f"Data Sources for {symbol}")
            
            if symbol in analysis_cache and "sources" in analysis_cache[symbol]:
                sources = analysis_cache[symbol]["sources"]
                
                if not sources:
                    st.write("No specific sources were mentioned in the analysis.")
                else:
                    # Sources from analysis text
                    st.markdown("### Sources Referenced in Analysis")
                    
                    for i, source in enumerate(sources):
                        with st.container():
                            cols = st.columns([3, 1, 7])
                            
                            # Source name and type
                            cols[0].markdown(f"**{source['Source']}**")
                            cols[1].markdown(f"*{source['Type']}*")
                            
                            # Source content with expandable area
                            with cols[2].expander("View Context"):
                                st.write(source.get("Content", "No context available"))
                            
                            st.markdown("---")
                
                # Show actual news articles
                if "news_data" in analysis_cache[symbol]:
                    news = analysis_cache[symbol]["news_data"]
                    if news:
                        st.markdown("### Recent News Articles")
                        
                        for article in news[:5]:  # Show top 5 articles
                            title = article.get("title", "No title")
                            source = article.get("source", {}).get("name", "Unknown source")
                            url = article.get("url", "#")
                            published = article.get("publishedAt", "")
                            description = article.get("description", "No description available")
                            
                            with st.container():
                                st.markdown(f"#### [{title}]({url})")
                                st.markdown(f"**Source:** {source}  |  **Published:** {published}")
                                st.write(description)
                                st.markdown("---")
            else:
                st.write(f"No analysis data available for {symbol}. Try analyzing it first.")
        
        if st.button("Close Sources"):
            st.session_state.show_sources = False

# Display sentiment modal
if "show_sentiment" in st.session_state and st.session_state.show_sentiment:
    with st.expander("Market Sentiment Analysis", expanded=True):
        if "viewing_symbol" in st.session_state:
            symbol = st.session_state.viewing_symbol
            
            if symbol in analysis_cache and "sentiment_metrics" in analysis_cache[symbol]:
                metrics = analysis_cache[symbol]["sentiment_metrics"]
                
                # Display overall sentiment
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    overall = metrics.get("overall", 50)
                    description = metrics.get("description", "Neutral")
                    
                    # Color based on sentiment
                    if overall >= 70:
                        st.markdown(f"<h2 style='text-align: center; color: green;'>{overall}%</h2>", unsafe_allow_html=True)
                    elif overall >= 50:
                        st.markdown(f"<h2 style='text-align: center; color: #3b82f6;'>{overall}%</h2>", unsafe_allow_html=True)
                    elif overall >= 30:
                        st.markdown(f"<h2 style='text-align: center; color: orange;'>{overall}%</h2>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h2 style='text-align: center; color: red;'>{overall}%</h2>", unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='text-align: center;'>{description} Sentiment for {symbol}</p>", unsafe_allow_html=True)
                
                # Show sentiment metrics
                st.markdown("### Sentiment Breakdown")
                
                for item in metrics.get("data", []):
                    # Determine color based on value
                    value = item.get("Value", 50)
                    if value >= 70:
                        bar_color = "green"
                    elif value >= 50:
                        bar_color = "#3b82f6"
                    elif value >= 30:
                        bar_color = "orange"
                    else:
                        bar_color = "red"
                    
                    # Create row with label, progress bar, and value
                    cols = st.columns([3, 8, 2])
                    cols[0].write(item["Category"])
                    cols[1].progress(value/100)
                    
                    # Value and trend
                    trend = item.get("Trend", "→")
                    trend_color = {"↑": "green", "→": "#f59e0b", "↓": "red"}.get(trend, "#f59e0b")
                    
                    cols[2].markdown(
                        f"<span style='color:{bar_color};'>{value}%</span> "
                        f"<span style='color:{trend_color};'>{trend}</span>", 
                        unsafe_allow_html=True
                    )
                
                # Show specific sentiment mentions
                if "mentions" in metrics and metrics["mentions"]:
                    st.markdown("### Specific Sentiment Mentions")
                    
                    for mention in metrics["mentions"]:
                        with st.container():
                            cols = st.columns([3, 2, 6])
                            cols[0].markdown(f"**{mention['Source']}**")
                            
                            # Style sentiment by value
                            sentiment_value = mention.get("Value", 50)
                            sentiment_text = mention.get("Sentiment", "Neutral")
                            
                            if sentiment_value >= 70:
                                cols[1].markdown(f"<span style='color: green;'>{sentiment_text.title()}</span>", unsafe_allow_html=True)
                            elif sentiment_value >= 50:
                                cols[1].markdown(f"<span style='color: #3b82f6;'>{sentiment_text.title()}</span>", unsafe_allow_html=True)
                            elif sentiment_value >= 30:
                                cols[1].markdown(f"<span style='color: orange;'>{sentiment_text.title()}</span>", unsafe_allow_html=True)
                            else:
                                cols[1].markdown(f"<span style='color: red;'>{sentiment_text.title()}</span>", unsafe_allow_html=True)
                            
                            with cols[2].expander("Context"):
                                st.write(mention.get("Context", "No context available"))
                
                # Show raw sentiment analysis
                with st.expander("View Full Sentiment Analysis"):
                    st.write(analysis_cache[symbol].get("sentiment_analysis", "No sentiment analysis available"))
            else:
                st.write(f"No sentiment data available for {symbol}. Try analyzing it first.")
        
        if st.button("Close Sentiment", key="close_sentiment_btn"):
            st.session_state.show_sentiment = False

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