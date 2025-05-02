# test_sentiment.py
import asyncio
import json
import sys
import os

# Add the parent directory to path to allow importing the sentiment_agent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Now import the SentimentAgent
from sentiment_agent import SentimentAgent

async def test_sentiment_analysis():
    agent = SentimentAgent()
    
    print("Testing sentiment analysis for ETH...")
    result = await agent.analyze_sentiment("ETH")
    
    # Pretty print the result
    print("\nSentiment Analysis Result:")
    print(f"Sentiment Score: {result['sentiment_score']}%")
    print(f"Sources Count: {result['sources_count']}")
    
    print("\nSources:")
    for idx, source in enumerate(result['sources']):
        print(f"{idx+1}. {source['name']} - {source['title']}")
        print(f"   URL: {source['url']}")
    
    print("\nAnalysis Text:")
    print(result['text'])

if __name__ == "__main__":
    asyncio.run(test_sentiment_analysis())