# data_agent.py

from openai import OpenAI
from polygon import RESTClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

class DataAgent:
    def __init__(self):
        # Initialize DataAgent with OpenAI and Polygon
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.polygon = RESTClient(api_key=os.getenv('POLYGON_API_KEY'))
        
    def get_market_data(self, symbol: str):
        """Get last 7 days of crypto market data"""
        # Set time range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Format dates
        end = end_date.strftime('%Y-%m-%d')
        start = start_date.strftime('%Y-%m-%d')
  
        print(f"\nFetching {symbol} data")
        print(f"From: {start}")
        print(f"To: {end}")
        
        # Get data from Polygon
        market_data = self.polygon.get_aggs(
            ticker=f"X:{symbol}USD",
            multiplier=1,
            timespan="day",
            from_=start,
            to=end,
            limit=7
        ) 

        
        return market_data, start, end

    async def analyze_crypto(self, crypto: str):
        """Analyze crypto with market data"""
        market_data, start_date, end_date = self.get_market_data(crypto)
        
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user", 
                    "content": f"""You are a crypto analyst. 
                    The data covers the period from {start_date} to {end_date}.
                    
                    Analyze this {crypto} market data: {market_data}. Make output concise and relevant
                    
                    Provide:
                    1. Current price and exact dates (most recent data point)
                    2. Volume analysis
                    3. Key observations
                    4. Short-term outlook
                    5. Simple price signal and prediction"""
                }
            ]
        )
        
        return completion.choices[0].message.content

# Test function
async def test():
    agent = DataAgent()
    print("Testing OpenAI...")
    result = await agent.analyze_crypto("SOL")
    print("\nAnalysis:", result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())