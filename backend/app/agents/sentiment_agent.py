# sentiment_agent.py

from openai import OpenAI
import requests
import tweepy  # Added for Twitter API
from dotenv import load_dotenv
import os
import re
from datetime import datetime, timedelta
import warnings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables
load_dotenv()

class SentimentAgent:
    def __init__(self):
        """Initialize the Sentiment Agent with necessary APIs and databases"""
        # Initialize OpenAI
        self.openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # News API configuration
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        # Twitter API configuration
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter client
        self.twitter_client = self._initialize_twitter()
        
        # Vector database setup - with graceful degradation
        self.vector_db = None
        self.embeddings = None
        
        # Try to initialize vector DB if dependencies are available
        try:
            from langchain_community.embeddings import OpenAIEmbeddings
            from langchain_community.vectorstores import Chroma
            
            self.embeddings = OpenAIEmbeddings()
            self.vector_db = self._initialize_vector_db()
        except ImportError:
            print("Vector database dependencies not available. Sentiment analysis will work without historical context.")
    
    def _initialize_twitter(self):
        """Initialize Twitter API client"""
        try:
            if self.twitter_bearer_token:
                client = tweepy.Client(bearer_token=self.twitter_bearer_token)
                print("Twitter client initialized successfully")
                return client
            else:
                print("Twitter bearer token not found. Twitter sentiment analysis will be unavailable.")
                return None
        except Exception as e:
            print(f"Error initializing Twitter client: {e}")
            return None
    
    def _initialize_vector_db(self):
        """Set up ChromaDB vector database"""
        try:
            # Try to import and use chromadb
            import chromadb
            from langchain_community.vectorstores import Chroma
            
            db = Chroma(
                collection_name="crypto_sentiment",
                embedding_function=self.embeddings
            )
            print("Vector database initialized successfully")
            return db
        except ImportError:
            print("ChromaDB not installed. Install it with 'pip install chromadb' for enhanced sentiment analysis.")
            return None
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
    
  

    async def get_twitter_data(self, symbol: str, limit: int = 10):
        """Fetch tweets about a cryptocurrency from the last 3 days only"""
        if not self.twitter_client:
            print("Twitter client not available")
            return {'tweets': [], 'sources': []}
        
        try:
            # Calculate date from 3 days ago in proper format
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
            # Add time filter to query
            query = f"#{symbol} -is:retweet since:{three_days_ago}"
            
            try:
                response = self.twitter_client.search_recent_tweets(
                    query=query,
                    max_results=limit,
                    tweet_fields=['created_at', 'public_metrics']
                )
                
                if response and response.data:
                    tweets = response.data
                    print(f"Found {len(tweets)} recent tweets (last 3 days) about {symbol}")
                    
                    # Process tweets as before...
                    formatted_tweets = []
                    tweet_sources = []
                    
                    for tweet in tweets:
                        # Get tweet metrics
                        metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
                        likes = metrics.get('like_count', 0)
                        retweets = metrics.get('retweet_count', 0)
                        
                        formatted_tweets.append({
                            'text': tweet.text,
                            'likes': likes,
                            'retweets': retweets,
                            'created_at': tweet.created_at
                        })
                        
                        tweet_url = f"https://twitter.com/twitter/status/{tweet.id}"
                        tweet_sources.append({
                            "name": "Twitter (Recent)",
                            "title": f"{tweet.text[:40]}...",
                            "url": tweet_url
                        })
                    
                    return {
                        'tweets': formatted_tweets,
                        'sources': tweet_sources
                    }
                else:
                    print(f"No recent tweets found for {symbol}")
                    return {'tweets': [], 'sources': []}
            except Exception as e:
                print(f"Twitter API error: {e}")
                return {'tweets': [], 'sources': []}
                
        except Exception as e:
            print(f"Error in Twitter processing: {e}")
            return {'tweets': [], 'sources': []}

    def store_in_vector_db(self, symbol: str, news_articles):
        """Store news data in vector database for future reference"""
        # Skip if vector DB initialization failed
        if not self.vector_db or not news_articles:
            return
            
        try:
            # Import necessary classes only if vector_db is available
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
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
        """Generate sentiment analysis with metadata for a cryptocurrency"""
        # Get news articles
        news = await self.get_news_data(symbol)
        self.store_in_vector_db(symbol, news)
        
        # Get Twitter data
        twitter_data = await self.get_twitter_data(symbol)
        
        # Format news and collect sources
        recent_news = []
        sources = []
        
        for article in news[:5]:
            title = article.get('title', 'No title')
            source = article.get('source', {}).get('name', 'Unknown source')
            url = article.get('url', '')
            
            recent_news.append(f"• {title} ({source})")
            
            if source and source != "Unknown source":
                sources.append({
                    "name": source,
                    "title": title,
                    "url": url
                })
        
        formatted_news = "\n".join(recent_news) if recent_news else "No recent news found"
        
        # Format Twitter data
        twitter_sentiment = ""
        if twitter_data['tweets']:
            tweet_texts = [f"• {tweet['text']}" for tweet in twitter_data['tweets']]
            twitter_sentiment = "\n".join(tweet_texts)
            
            # Add Twitter sources
            sources.extend(twitter_data['sources'])
        
        # Generate analysis
        completion = self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a cryptocurrency sentiment analyzer. Your analysis must end with a sentiment score in the format [SENTIMENT_SCORE: XX%] where 0-40% is bearish, 41-59% is neutral, and 60-100% is bullish."
                },
                {
                    "role": "user", 
                    "content": f"""Analyze these news articles and tweets about {symbol}:

    NEWS ARTICLES:
    {formatted_news}
    
    TWITTER SENTIMENT:
    {twitter_sentiment}

    Provide:
    1. Overall sentiment (bullish/bearish/neutral)
    2. Key topics being discussed
    3. Notable news impact
    4. Social media sentiment analysis
    5. How sentiment might affect price
    6. Regulatory insights

    END YOUR ANALYSIS WITH: [SENTIMENT_SCORE: XX%] where XX matches your written analysis.
    - Very bearish: 0-20%
    - Somewhat bearish: 21-40%
    - Neutral: 41-59%
    - Somewhat bullish: 60-80%
    - Very bullish: 81-100%

    Your score should precisely reflect the strength of sentiment in your analysis."
    """
                }
            ],
            temperature=0.2
        )
        
        analysis_text = completion.choices[0].message.content
        
        # Extract sentiment score
        sentiment_score = 50
        score_match = re.search(r'\[SENTIMENT_SCORE:\s*(\d+)%\]', analysis_text)
        if score_match:
            try:
                sentiment_score = int(score_match.group(1))
                sentiment_score = max(0, min(100, sentiment_score))
                analysis_text = analysis_text.replace(score_match.group(0), "")
            except ValueError:
                pass
        
        return {
            "text": analysis_text,
            "sentiment_score": sentiment_score,
            "sources": sources,
            "sources_count": len(sources)
        }

# Test function
async def test():
    agent = SentimentAgent()
    print("Testing sentiment analysis...")
    result = await agent.analyze_sentiment("BTC")
    print("\nAnalysis:", result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())