# sentiment_agent.py

from openai import OpenAI
import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

class SentimentAgent:
    def __init__(self):
        """Initialize the Sentiment Agent with necessary APIs and databases"""
        # Initialize OpenAI
        self.openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # News API configuration
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        # Vector database setup
        self.embeddings = OpenAIEmbeddings()
        self.vector_db = self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Set up ChromaDB vector database"""
        try:
            db = Chroma(
                collection_name="crypto_sentiment",
                embedding_function=self.embeddings
            )
            print("Vector database initialized successfully")
            return db
        except Exception as e:
            print(f"Error initializing vector database: {e}")
            return None

    async def get_news_data(self, symbol: str, limit: int = 20):
        """Fetch recent news articles about a cryptocurrency"""
        # Prepare request parameters
        params = {
            'q': f"{symbol} cryptocurrency",
            'apiKey': self.news_api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit
        }
        
        url = "https://newsapi.org/v2/everything"
        
        try:
            # Make API request
            response = requests.get(url, params=params)
            data = response.json()
            
            # Process response
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                print(f"Found {len(articles)} news articles about {symbol}")
                return articles
            else:
                print(f"News API error: {data.get('message')}")
                return []
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def store_in_vector_db(self, symbol: str, news_articles):
        """Store news data in vector database for future reference"""
        # Skip if vector DB initialization failed
        if not self.vector_db or not news_articles:
            return
            
        try:
            # Format news articles for storage
            formatted_articles = []
            for article in news_articles:
                title = article.get('title', '')
                desc = article.get('description', '')
                content = article.get('content', '')
                formatted_articles.append(f"TITLE: {title}\nDESCRIPTION: {desc}\nCONTENT: {content}")
            
            news_content = "\n\n".join(formatted_articles)
            
            # Split content into manageable chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.split_text(news_content)
            
            if not chunks:
                print("No content to store after processing")
                return
                
            # Prepare documents with metadata
            today = datetime.now().strftime("%Y-%m-%d")
            docs = [
                {"page_content": chunk, "metadata": {"symbol": symbol, "date": today}}
                for chunk in chunks
            ]
            
            # Store in vector database
            self.vector_db.add_documents(docs)
            print(f"Stored {len(chunks)} document chunks in vector database")
            
        except Exception as e:
            print(f"Error storing data in vector database: {e}")

    def retrieve_historical_context(self, symbol: str):
        """Retrieve relevant historical data from vector database"""
        if not self.vector_db:
            return []
            
        try:
            results = self.vector_db.similarity_search(
                f"{symbol} cryptocurrency market sentiment",
                k=5
            )
            
            if results:
                print(f"Retrieved {len(results)} relevant historical documents")
                return [doc.page_content for doc in results]
            else:
                print("No relevant historical data found")
                return []
                
        except Exception as e:
            print(f"Error retrieving historical data: {e}")
            return []

    async def analyze_sentiment(self, symbol: str):
        """Generate comprehensive sentiment analysis for a cryptocurrency"""
        # Gather news data
        news = await self.get_news_data(symbol)
        
        # Store for future reference
        self.store_in_vector_db(symbol, news)
        
        # Get historical context
        historical_data = self.retrieve_historical_context(symbol)
        
        # Format data for display
        recent_news = []
        for article in news[:5]:
            title = article.get('title', 'No title')
            source = article.get('source', {}).get('name', 'Unknown source')
            recent_news.append(f"• {title} ({source})")
        
        formatted_news = "\n".join(recent_news) if recent_news else "No recent news found"
        
        # Generate analysis with o1-preview model
        completion = self.openai.chat.completions.create(
            model="o1-preview",
            messages=[
                {
                    "role": "user", 
                    "content": f"""You are a cryptocurrency sentiment analyst. Your task is to analyze the provided news articles about {symbol}.
                    
                    Analyze these news articles about {symbol}:
                    
                    {formatted_news}
                    
                    Please ignore any dates in the articles and analyze them as if they are current news.

                    Give links for data sources.
                    Provide a sentiment score
                    
                    Provide:
                    (be concise and relevant)
                    quote any relevant news source or tweet that is relevant to the analysis
                    1. Overall sentiment (bullish/bearish/neutral)
                    2. Key topics being discussed
                    3. Notable news impact
                    4. How sentiment might affect price
                    5. Regulatory or policy-related insights
                    """
                }
            ]
        )
    
        return completion.choices[0].message.content

# Test function
async def test():
    agent = SentimentAgent()
    print("Testing sentiment analysis...")
    result = await agent.analyze_sentiment("BTC")
    print("\nAnalysis:", result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())