# main_agent.py

from openai import OpenAI
import asyncio
import os
from dotenv import load_dotenv
from data_agent import DataAgent
from sentiment_agent import SentimentAgent

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
        sentiment_analysis = await self.sentiment_agent.analyze_sentiment(symbol)
        
        # Store context for follow-up questions
        self.context[symbol] = {
            "market": market_analysis,
            "sentiment": sentiment_analysis
        }
        
        # Combine both analyses
        print("Generating insights...")
        combined_analysis = await self.combine_analyses(symbol, market_analysis, sentiment_analysis)
        
        return combined_analysis
    
    async def handle_followup(self, symbol: str, question: str):
        """Handle follow-up questions about a cryptocurrency"""
        if symbol not in self.context:
            return f"I don't have any analysis for {symbol} yet. Would you like me to analyze it?"
        
        context = self.context[symbol]
        completion = self.client.chat.completions.create(
            model="o1-preview",
            messages=[
                {
                    "role": "user",
                    "content": f"""You are Cryptosys. You've previously analyzed {symbol} with this information:
                    
                    MARKET ANALYSIS:
                    {context['market']}
                    
                    SENTIMENT ANALYSIS:
                    {context['sentiment']}
                    
                    The user is asking: "{question}"
                    
                    Answer their question concisely based on your analysis, unless they specifically ask for detailed information."""
                }
            ]
        )
        
        return completion.choices[0].message.content
    
    async def combine_analyses(self, symbol: str, market_analysis: str, sentiment_analysis: str):
        """Combine market and sentiment analyses into a conversational response"""
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""You are Cryptosys, a helpful and conversational AI crypto analyst. Your tone is friendly but professional.
                    
                    You've analyzed {symbol} and need to present your findings concisely. Here's the data:
                    
                    TECHNICAL ANALYSIS:
                    {market_analysis}
                    
                    SENTIMENT ANALYSIS:
                    {sentiment_analysis}
                    
                    Respond conversationally as if you're talking directly to the user. Include:
                    
                    1. A brief greeting with {symbol}'s current price and trend
                    2. Key insights from technical and sentiment analysis
                    3. Where the data agrees or conflicts
                    4. Your overall assessment and recommendation
                    
                    Keep your response concise and easy to understand. Use short paragraphs and occasional bullet points.
                    """
                }
            ]
        )
        
        return completion.choices[0].message.content

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
                analysis = await system.get_complete_analysis(current_symbol)
                print(f"\n{analysis}")
            except Exception as e:
                print(f"\nI couldn't analyze {current_symbol}. Error: {e}")
                current_symbol = None
        else:
            # Handle follow-up question
            try:
                response = await system.handle_followup(current_symbol, user_input)
                print(f"\n{response}")
            except Exception as e:
                print(f"\nI couldn't answer that question. Error: {e}")

if __name__ == "__main__":
    asyncio.run(chat())