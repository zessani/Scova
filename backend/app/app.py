# app.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import traceback
from dotenv import load_dotenv
from agents.data_agent import DataAgent
from agents.sentiment_agent import SentimentAgent
from agents.main_agent import CryptoAnalysisSystem
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Cryptosys API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We'll restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
data_agent = DataAgent()
sentiment_agent = SentimentAgent()
analysis_system = CryptoAnalysisSystem()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Cache for analysis results
analysis_cache = {}

# Pydantic models for request validation
class FollowUpRequest(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    question: str = Field(..., description="User's follow-up question")

class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    timeframe: str = Field("month", description="Prediction timeframe: 'week', 'month', or '3months'")

class TradingStrategyRequest(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    goal: str = Field(..., description="User's investment goal, e.g., 'maximize profit in 3 months'")

class PolicyImpactRequest(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    policy_description: str = Field(..., description="Description of the policy or regulation")

@app.get("/")
async def root():
    return {"message": "Welcome to Cryptosys API"}

@app.get("/api/analyze/{symbol}")
async def analyze_crypto(symbol: str):
    """Get comprehensive analysis for a cryptocurrency with sentiment data"""
    symbol = symbol.upper()
    
    if symbol in analysis_cache:
        return analysis_cache[symbol]
    
    try:
        result = await analysis_system.get_complete_analysis(symbol)
        
        analysis_cache[symbol] = {
            "symbol": symbol,
            "market_analysis": result.get("market_analysis", ""),
            "sentiment_analysis": result.get("sentiment_analysis", ""),
            "combined_analysis": result.get("combined_analysis", ""),
            "sentiment_score": result.get("sentiment_score", 50),
            "sources": result.get("sources", []),
            "sources_count": result.get("sources_count", 0)
        }
        
        return analysis_cache[symbol]
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error analyzing {symbol}: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error analyzing {symbol}: {str(e)}")

@app.post("/api/followup")
async def handle_followup(request: FollowUpRequest):
    """Handle follow-up questions about a cryptocurrency with sentiment data"""
    symbol = request.symbol.upper()
    question = request.question
    
    if symbol not in analysis_cache:
        raise HTTPException(status_code=404, detail=f"No analysis found for {symbol}")
    
    try:
        # Get the cached analysis for context
        cached = analysis_cache[symbol]
        
        # Create context for the main agent if it doesn't exist
        if symbol not in analysis_system.context:
            analysis_system.context[symbol] = {
                "market": cached["market_analysis"],
                "sentiment": cached["sentiment_analysis"],
                "sentiment_score": cached.get("sentiment_score", 50),
                "sources": cached.get("sources", [])
            }
        
        # Use the main agent to handle the follow-up
        result = await analysis_system.handle_followup(symbol, question)
        
        return {
            "symbol": symbol,
            "question": question,
            "response": result.get("response", ""),
            "sentiment_score": result.get("sentiment_score", 50),
            "sources": result.get("sources", []),
            "sources_count": result.get("sources_count", 0)
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error handling follow-up: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error handling follow-up: {str(e)}")

@app.post("/api/predict")
async def predict_price(request: PredictionRequest):
    """Generate price movement prediction for a specific timeframe with sentiment data"""
    symbol = request.symbol.upper()
    timeframe = request.timeframe
    
    # Ensure we have basic analysis first
    if symbol not in analysis_cache:
        try:
            # Get initial analysis
            await analyze_crypto(symbol)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing {symbol} prior to prediction: {str(e)}")
    
    try:
        # Generate prediction using the main agent
        result = await analysis_system.predict_price_movement(symbol, timeframe)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "prediction": result.get("prediction", ""),
            "sentiment_score": result.get("sentiment_score", 50),
            "sources": result.get("sources", []),
            "sources_count": result.get("sources_count", 0)
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error generating prediction: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")

@app.post("/api/strategy")
async def trading_strategy(request: TradingStrategyRequest):
    """Generate optimal investment strategy based on user's goal with sentiment data"""
    symbol = request.symbol.upper()
    goal = request.goal
    
    # Ensure we have basic analysis first
    if symbol not in analysis_cache:
        try:
            # Get initial analysis
            await analyze_crypto(symbol)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing {symbol} prior to strategy: {str(e)}")
    
    try:
        # Generate strategy using the main agent
        result = await analysis_system.optimal_trading_strategy(symbol, goal)
        
        return {
            "symbol": symbol,
            "goal": goal,
            "strategy": result.get("strategy", ""),
            "sentiment_score": result.get("sentiment_score", 50),
            "sources": result.get("sources", []),
            "sources_count": result.get("sources_count", 0)
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error generating strategy: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error generating strategy: {str(e)}")

@app.post("/api/policy-impact")
async def policy_impact(request: PolicyImpactRequest):
    """Analyze how a policy or regulation might impact a cryptocurrency with sentiment data"""
    symbol = request.symbol.upper()
    policy_description = request.policy_description
    
    try:
        # Generate analysis using the main agent
        result = await analysis_system.analyze_policy_impact(symbol, policy_description)
        
        return {
            "symbol": symbol,
            "policy_description": policy_description,
            "impact_analysis": result.get("impact_analysis", ""),
            "sentiment_score": result.get("sentiment_score", 50),
            "sources": result.get("sources", []),
            "sources_count": result.get("sources_count", 0)
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error analyzing policy impact: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error analyzing policy impact: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)