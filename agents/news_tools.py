import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import tool
import requests
from config.config import NEWS_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_news(query: str, is_crypto: bool = True) -> List[Dict[str, Any]]:
    """Generic function to fetch news from NewsAPI."""
    try:
        if not NEWS_API_KEY:
            logger.error("No NewsAPI key found! Please check your .env file.")
            return []
            
        base_url = "https://newsapi.org/v2/"
        endpoint = "everything" if is_crypto else "top-headlines"
        
        # Calculate date for the last 24 hours
        from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        headers = {
            'X-Api-Key': NEWS_API_KEY,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        params = {
            'language': 'en',
            'pageSize': 5,
            'sortBy': 'publishedAt',
            'from': from_date,
            'apiKey': NEWS_API_KEY  # Some versions of NewsAPI require this as a query param
        }
        
        # Log the request details (without the full API key)
        logger.info(f"Making request to {base_url}{endpoint}")
        logger.info(f"Params: { {k: v for k, v in params.items() if k != 'apiKey'} }")
        
        if is_crypto:
            params['q'] = f"{query} AND (bitcoin OR ethereum OR crypto OR blockchain)"
        else:
            # For stock news, use a simpler query to avoid complex syntax issues
            params['q'] = f"{query} OR stocks OR market"
            params['category'] = 'business'
        
        logger.info(f"Fetching {'crypto' if is_crypto else 'stock'} news with query: {query}")
        # Try with headers first, then fall back to query param if needed
        try:
            response = requests.get(
                f"{base_url}{endpoint}",
                headers=headers,
                params={k: v for k, v in params.items() if k != 'apiKey'},  # Don't send apiKey in both places
                timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.warning(f"Request with headers failed ({http_err}), trying with API key in query params...")
            # Try again with API key in query params
            response = requests.get(
                f"{base_url}{endpoint}",
                params=params,  # This includes apiKey
                timeout=10
            )
            response.raise_for_status()
        response.raise_for_status()
        
        articles = response.json().get('articles', [])
        logger.info(f"Found {len(articles)} articles")
        return articles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

def get_crypto_news() -> str:
    """Return top 5 cryptocurrency news headlines from the last 24 hours."""
    articles = fetch_news("cryptocurrency", is_crypto=True)
    
    if not articles:
        logger.warning("No crypto news articles found")
        return "No cryptocurrency news available at the moment. Please try again later."
        
    result = [
        f"{i+1}. {article['title']} ({article['source']['name']}) - {article['url']}"
        for i, article in enumerate(articles)
    ]
    return "\n".join(result)

def get_stock_news() -> str:
    """Return top 5 stock market news headlines from the last 24 hours."""
    articles = fetch_news("stock market", is_crypto=False)
    
    if not articles:
        logger.warning("No stock news articles found")
        return "No stock market news available at the moment. Please try again later."
        
    result = [
        f"{i+1}. {article['title']} ({article['source']['name']}) - {article['url']}"
        for i, article in enumerate(articles)
    ]
    return "\n".join(result)

# LangChain tool wrappers for agent usage
get_crypto_news_tool = tool("get_crypto_news")(get_crypto_news)
get_stock_news_tool = tool("get_stock_news")(get_stock_news)