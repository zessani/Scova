# app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from agents.data_agent import DataAgent
from agents.sentiment_agent import SentimentAgent
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Cryptosys API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_agent = DataAgent()
sentiment_agent = SentimentAgent()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
analysis_cache = {}

class FollowUpRequest(BaseModel):
    symbol: str
    question: str

@app.get("/")
async def root():
    return {"message": "Welcome to Cryptosys API"}

@app.get("/api/analyze/{symbol}")
async def analyze_crypto(symbol: str):
    symbol = symbol.upper()
    
    if symbol in analysis_cache:
        return analysis_cache[symbol]
    
    try:
        market_analysis = await data_agent.analyze_crypto(symbol)
        sentiment_analysis = await sentiment_agent.analyze_sentiment(symbol)
        combined_analysis = await generate_combined_analysis(symbol, market_analysis, sentiment_analysis)
        
        analysis_cache[symbol] = {
            "symbol": symbol,
            "market_analysis": market_analysis,
            "sentiment_analysis": sentiment_analysis,
            "combined_analysis": combined_analysis
        }
        
        return analysis_cache[symbol]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing {symbol}: {str(e)}")

@app.post("/api/followup")
async def handle_followup(request: FollowUpRequest):
    symbol = request.symbol.upper()
    question = request.question
    
    if symbol not in analysis_cache:
        raise HTTPException(status_code=404, detail=f"No analysis found for {symbol}")
    
    try:
        cached = analysis_cache[symbol]
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""You are Cryptosys. You previously analyzed {symbol} with this information:
                    
                    MARKET ANALYSIS:
                    {cached['market_analysis']}
                    
                    SENTIMENT ANALYSIS:
                    {cached['sentiment_analysis']}
                    
                    The user is asking: "{question}"
                    
                    Answer concisely based on your analysis."""
                }
            ]
        )
        
        return {
            "symbol": symbol,
            "question": question,
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling follow-up: {str(e)}")

async def generate_combined_analysis(symbol: str, market_analysis: str, sentiment_analysis: str):
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""You are Cryptosys analyzing {symbol}. Here's the data:
                    
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
        
        return completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error generating combined analysis: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)