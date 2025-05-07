# main_agent.py

from openai import OpenAI
import asyncio
import os
import json
import re
from dotenv import load_dotenv
from agents.data_agent import DataAgent
from agents.sentiment_agent import SentimentAgent
from datetime import datetime, timedelta

load_dotenv()

class CryptoAnalysisSystem:
    def __init__(self):
        """Initialize the complete crypto analysis system"""
        self.data_agent = DataAgent()
        self.sentiment_agent = SentimentAgent()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.context = {}
    
    async def get_complete_analysis(self, symbol: str):
        """Get complete analysis combining market data and sentiment"""
        # Get technical analysis from data agent
        print(f"Analyzing market data for {symbol}...")
        market_analysis = await self.data_agent.analyze_crypto(symbol)
        
        # Get sentiment analysis from sentiment agent
        print(f"Analyzing market sentiment for {symbol}...")
        sentiment_result = await self.sentiment_agent.analyze_sentiment(symbol)
        sentiment_analysis = sentiment_result["text"]
        
        # Store context for follow-up questions
        self.context[symbol] = {
            "market": market_analysis,
            "sentiment": sentiment_analysis,
            "sentiment_score": sentiment_result["sentiment_score"],
            "sources": sentiment_result["sources"]
        }
        
        # Combine both analyses
        print("Generating insights...")
        combined_analysis = await self.combine_analyses(symbol, market_analysis, sentiment_analysis)
        
        # Return combined analysis with metadata
        return {
            "combined_analysis": combined_analysis,
            "market_analysis": market_analysis,
            "sentiment_analysis": sentiment_analysis,
            "sentiment_score": sentiment_result["sentiment_score"],
            "sources": sentiment_result["sources"],
            "sources_count": sentiment_result["sources_count"]
        }
    
    async def handle_followup(self, symbol: str, question: str):
        """Handle follow-up questions about a cryptocurrency"""
        if symbol not in self.context:
            return {
                "response": f"I don't have any analysis for {symbol} yet. Would you like me to analyze it?",
                "sentiment_score": 50,
                "sources": [],
                "sources_count": 0
            }
        
        context = self.context[symbol] 
        
        # Extract if this is a timing/action question
        timing_keywords = ["when", "time", "best", "optimal", "should i buy", "should i sell", "maximize"]
        is_timing_question = any(keyword in question.lower() for keyword in timing_keywords)
        
        # Complex timing questions use o1-preview for better reasoning
        model_to_use = "gpt-4"  # Default to GPT-4 for most queries
        
        if is_timing_question:
            model_to_use = "gpt-4"  # Use GPT-4 for timing questions since it supports the prompt format we're using
        
        prompt_content = f"""You are Cryptosys. You've previously analyzed {symbol} with this information:
        
        MARKET ANALYSIS:
        {context['market']}
        
        SENTIMENT ANALYSIS:
        {context['sentiment']}
        
        The user is asking: "{question}"
        
        Answer their question directly and specifically. """
        
        if is_timing_question:
            prompt_content += """Provide EXACT recommendations with:
            1. Specific timeframes (e.g., "May 10-15" or "next Tuesday-Friday")
            2. Specific price targets or ranges when appropriate
            3. Clear action steps
            
            Be direct and concise - get straight to the point with what they should do and when.
            """
        else:
            prompt_content += """Be concise and directly answer their specific question.
            Only provide relevant information that directly answers their question.
            
            If they want detailed analysis, provide it - otherwise, be brief and to the point.
            """
        
        prompt_content += "\nInclude a brief disclaimer at the end that this is for informational purposes only."
        
        completion = self.client.chat.completions.create(
            model=model_to_use,
            messages=[
                {
                    "role": "user",
                    "content": prompt_content
                }
            ]
        )
        
        return {
            "response": completion.choices[0].message.content,
            "sentiment_score": context.get("sentiment_score", 50),
            "sources": context.get("sources", []),
            "sources_count": len(context.get("sources", []))
        }
    
    async def combine_analyses(self, symbol: str, market_analysis: str, sentiment_analysis: str):
        """Combine market and sentiment analyses into a conversational response"""
        completion = self.client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for analysis synthesis
            messages=[
                {
                    "role": "user",
                    "content": f"""You are Cryptosys, a helpful and conversational AI crypto analyst. Your tone is friendly but professional.
                    
                    You've analyzed {symbol} and need to present your findings concisely. Here's the data:
                    
                    TECHNICAL ANALYSIS:
                    {market_analysis}
                    
                    SENTIMENT ANALYSIS:
                    {sentiment_analysis}
                    
                    Respond with a concise summary that includes:
                    1. Current price and primary trend
                    2. 1-2 key insights from technical and sentiment analysis
                    3. Your overall assessment
                    
                    Keep your response under 200 words, unless the user has specifically requested detailed analysis.
                    """
                }
            ]
        )
        
        return completion.choices[0].message.content
    
    async def predict_price_movement(self, symbol: str, timeframe: str):
        """
        Predict price movement for a cryptocurrency over a specific timeframe
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            timeframe: Time period for prediction ('week', 'month', '3months')
            
        Returns:
            Prediction information as a dictionary
        """
        # Get market data from data agent
        market_data, start_date, end_date = self.data_agent.get_market_data(symbol)
        
        # Get sentiment data with structured result
        sentiment_result = await self.sentiment_agent.analyze_sentiment(symbol)
        sentiment_analysis = sentiment_result["text"]
        
        # Map timeframe to days for prediction
        timeframe_days = {
            'week': 7,
            'month': 30,
            '3months': 90
        }
        days = timeframe_days.get(timeframe, 30)  # Default to 30 days
        target_date = datetime.now() + timedelta(days=days)
        
        # Current date formatted for the prompt
        current_date_str = datetime.now().strftime('%B %d, %Y')
        target_date_str = target_date.strftime('%B %d, %Y')
        
        # Generate prediction using GPT-4
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a crypto market expert for Cryptosys. Today's date is {current_date_str}. When referring to dates, always use human-readable format like 'May 5' or 'next Monday', never use timestamps.
                    
                    Based on this market data:
                    
                    {market_data}
                    
                    And this sentiment analysis:
                    
                    {sentiment_analysis}
                    
                    Provide a specific price prediction for {symbol} by {target_date_str} ({days} days).
                    
                    Your response should include:
                    1. Exact price range prediction (low-high)
                    2. Most likely price point with date ranges for when it might be reached
                    3. Specific dates or time periods to watch for significant price movements
                    4. Clear recommendation (buy, sell, or hold) with exact timing suggestions
                    
                    Be specific, direct, and concise. Provide exact numbers and dates. Include a brief disclaimer at the end.
                    """
                }
            ]
        )
        
        return {
            "prediction": completion.choices[0].message.content,
            "sentiment_score": sentiment_result["sentiment_score"],
            "sources": sentiment_result["sources"],
            "sources_count": sentiment_result["sources_count"]
        }
    
    async def optimal_trading_strategy(self, symbol: str, goal: str):
        """
        Generate investment strategy based on user's goal
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            goal: User's investment goal (e.g., 'maximize profit in 3 months')
            
        Returns:
            Strategy analysis as a dictionary
        """
        # Get market data from data agent
        market_data, start_date, end_date = self.data_agent.get_market_data(symbol)
        
        # Get sentiment data with structured result
        sentiment_result = await self.sentiment_agent.analyze_sentiment(symbol)
        sentiment_analysis = sentiment_result["text"]
        
        # Extract the timeframe from the question
        timeframe_matches = re.search(r'(\d+)\s*(day|week|month|year)s?', goal.lower())
        days = 30  # Default to one month
        
        if timeframe_matches:
            amount = int(timeframe_matches.group(1))
            unit = timeframe_matches.group(2)
            if unit == "day":
                days = amount
            elif unit == "week":
                days = amount * 7
            elif unit == "month":
                days = amount * 30
            elif unit == "year":
                days = amount * 365
        
        # Extract action from the question
        action = "hold"  # Default to hold recommendation
        if "sell" in goal.lower():
            action = "sell"
        elif "buy" in goal.lower():
            action = "buy"
        
        # Get current date for reference
        current_date = datetime.now()
        current_date_str = current_date.strftime('%B %d, %Y')
        
        # Generate a response using GPT-4
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a critical, intelligent crypto analyst. The current date is {current_date_str}.
                    When analyzing investment strategies, consider ALL options:
                    1. Buying more if that's the best strategy
                    2. Selling if that's the best strategy
                    3. Holding if that's the best strategy
                    4. A mixed approach with specific timing
                    
                    Always match your response to the FULL timeframe the user mentioned.
                    Be willing to challenge the user's assumptions if they're asking about an action that isn't optimal.
                    
                    When referring to dates, always use human-readable format like 'May 5' or 'next Monday', never use timestamps.
                    
                    Based on this market data:
                    
                    {market_data}
                    
                    And this sentiment analysis:
                    
                    {sentiment_analysis}
                    
                    The user asked: "{goal}"
                    
                    Provide a comprehensive, intelligent strategy for {symbol} over the FULL {days}-day period mentioned.
                    
                    Think critically about whether the action the user asked about (buying, selling, timing) is actually the BEST approach given the data. If a different approach would be better, explain why.
                    
                    Include:
                    1. Whether buying, selling, holding, or a mixed approach is best for maximum returns
                    2. Specific timing recommendations across the FULL timeframe with exact dates
                    3. Price targets and signals to watch for
                    4. Clear explanation of WHY you're making these recommendations
                    5. Different scenarios and how the user should respond to each
                    
                    Use the first paragraph to directly answer whether they should take the action they asked about, or if a different approach would be better for maximum returns.
                    """
                }
            ]
        )
        
        return {
            "strategy": completion.choices[0].message.content,
            "sentiment_score": sentiment_result["sentiment_score"],
            "sources": sentiment_result["sources"],
            "sources_count": sentiment_result["sources_count"]
        }
    
    async def analyze_policy_impact(self, symbol: str, policy_description: str):
        """
        Analyze how a policy or regulation might impact a cryptocurrency
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            policy_description: Description of the policy/regulation
            
        Returns:
            Impact analysis as a dictionary
        """
        # Get current market data
        market_data, start_date, end_date = self.data_agent.get_market_data(symbol)
        
        # Get sentiment data with structured result
        sentiment_result = await self.sentiment_agent.analyze_sentiment(symbol)
        
        # Get current date for reference
        current_date_str = datetime.now().strftime('%B %d, %Y')
        
        # Generate analysis using GPT-4
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""You are Cryptosys, a crypto regulatory analysis expert. Today's date is {current_date_str}. When referring to dates, always use human-readable format like 'May 5' or 'next Monday', never use timestamps.
                    
                    Analyze how this policy might impact {symbol}:
                    
                    POLICY DESCRIPTION:
                    {policy_description}
                    
                    MARKET DATA:
                    {market_data}
                    
                    Provide a specific impact analysis with:
                    1. Immediate impact (next 7 days)
                    2. Medium-term impact (1-3 months)
                    3. Long-term impact (beyond 3 months)
                    4. Expected price effects (percentage and dollar amounts)
                    5. How this might affect market sentiment
                    6. Specific recommendations for investors
                    
                    Be direct, specific, and concise. Include a brief disclaimer at the end.
                    """
                }
            ]
        )
        
        return {
            "impact_analysis": completion.choices[0].message.content,
            "sentiment_score": sentiment_result["sentiment_score"],
            "sources": sentiment_result["sources"],
            "sources_count": sentiment_result["sources_count"]
        }

async def chat():
    system = CryptoAnalysisSystem()
    current_symbol = None
    
    print("\nWelcome to Cryptosys! I can analyze cryptocurrencies and provide insights.")
    print("Type 'exit' to quit, 'new' for a different crypto.\n")
    
    while True:
        if current_symbol:
            user_input = input(f"\nAsk me about {current_symbol} (or 'new'/'exit'): ")
        else:
            user_input = input("\nWhat cryptocurrency would you like to analyze? (e.g., BTC, ETH): ")
        
        if user_input.lower() == 'exit':
            print("\nThank you for using Cryptosys. Goodbye!")
            break
            
        if user_input.lower() == 'new':
            current_symbol = None
            continue
            
        if not current_symbol:
            current_symbol = user_input.upper()
            print(f"\nAnalyzing {current_symbol}. This will take a moment...")
            
            try:
                result = await system.get_complete_analysis(current_symbol)
                print(f"\n{result['combined_analysis']}")
                print(f"\nSentiment Score: {result['sentiment_score']}%")
                print(f"Sources: {result['sources_count']}")
            except Exception as e:
                print(f"\nI couldn't analyze {current_symbol}. Error: {e}")
                current_symbol = None
        else:
            # Check for prediction or strategy requests
            if "predict" in user_input.lower() or "forecast" in user_input.lower():
                timeframe = "month"  # Default
                
                if "week" in user_input.lower():
                    timeframe = "week"
                elif "3 month" in user_input.lower() or "three month" in user_input.lower():
                    timeframe = "3months"
                
                try:
                    print(f"\nGenerating price analysis for {current_symbol} over {timeframe}...")
                    result = await system.predict_price_movement(current_symbol, timeframe)
                    print(f"\n{result['prediction']}")
                    print(f"\nSentiment Score: {result['sentiment_score']}%")
                    print(f"Sources: {result['sources_count']}")
                except Exception as e:
                    print(f"\nI couldn't generate a price analysis. Error: {e}")
            
            elif any(phrase in user_input.lower() for phrase in ["when should i", "strategy", "timing", "best time", "maximize"]):
                try:
                    print(f"\nDeveloping investment strategy...")
                    result = await system.optimal_trading_strategy(current_symbol, user_input)
                    print(f"\n{result['strategy']}")
                    print(f"\nSentiment Score: {result['sentiment_score']}%")
                    print(f"Sources: {result['sources_count']}")
                except Exception as e:
                    print(f"\nI couldn't generate an investment strategy. Error: {e}")
            
            elif any(phrase in user_input.lower() for phrase in ["policy", "regulation", "impact", "affect"]):
                try:
                    print(f"\nAnalyzing potential impact...")
                    result = await system.analyze_policy_impact(current_symbol, user_input)
                    print(f"\n{result['impact_analysis']}")
                    print(f"\nSentiment Score: {result['sentiment_score']}%")
                    print(f"Sources: {result['sources_count']}")
                except Exception as e:
                    print(f"\nI couldn't analyze the impact. Error: {e}")
            
            else:
                # Handle regular follow-up question
                try:
                    result = await system.handle_followup(current_symbol, user_input)
                    print(f"\n{result['response']}")
                    print(f"\nSentiment Score: {result['sentiment_score']}%")
                    print(f"Sources: {result['sources_count']}")
                except Exception as e:
                    print(f"\nI couldn't answer that question. Error: {e}")

if __name__ == "__main__":
    asyncio.run(chat())