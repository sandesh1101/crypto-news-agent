import os
import schedule
import time
import logging
import pytz
from datetime import datetime, time as dt_time
from typing import Optional, List, Dict, Any, Callable
from dotenv import load_dotenv
from agents.news_tools import get_crypto_news, get_stock_news

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Timezone configuration
TARGET_TIMEZONE = pytz.timezone('America/New_York')
SCHEDULE_TIME = dt_time(7, 0)  # 7:00 AM

def get_current_time() -> datetime:
    """Get current time in target timezone."""
    return datetime.now(TARGET_TIMEZONE)

def format_news(news_items: List[Dict[str, Any]], news_type: str) -> str:
    """Format news items with titles, sources, and summaries."""
    if not news_items:
        return f"No {news_type.lower()} news available at the moment."
    
    timestamp = get_current_time().strftime('%Y-%m-%d %H:%M')
    header = f"\n{'='*10} {news_type.upper()} NEWS - {timestamp} {'='*10}\n"
    
    formatted_news = []
    for i, item in enumerate(news_items, 1):
        title = item.get('title', 'No title')
        source = item.get('source', {}).get('name', 'Unknown source')
        url = item.get('url', '#')
        summary = item.get('summary', 'No summary available')
        
        formatted = (
            f"{i}. {title} ({source})\n"
            f"   URL: {url}\n"
            f"   Summary: {summary}\n"
        )
        formatted_news.append(formatted)
    
    return header + '\n'.join(formatted_news)

def get_news() -> str:
    """Fetch and return news, trying crypto first, then stock if crypto fails."""
    try:
        # Try to get crypto news first
        crypto_news = get_crypto_news()
        if crypto_news and isinstance(crypto_news, list) and len(crypto_news) > 0:
            return format_news(crypto_news, "CRYPTO")
            
        # Fall back to stock news
        stock_news = get_stock_news()
        if stock_news and isinstance(stock_news, list) and len(stock_news) > 0:
            return format_news(stock_news, "STOCK")
            
        return "No news available at the moment."
        
    except Exception as e:
        error_msg = f"Error fetching news: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

def run_daily_agent() -> None:
    """Fetch and save top crypto or stock news to a file."""
    current_time = get_current_time()
    logger.info(f"Running news agent at {current_time}")
    
    try:
        news = get_news()
        
        # Ensure output directory exists
        news_output_dir = os.getenv('NEWS_OUTPUT_DIR', 'news_output')
        os.makedirs(news_output_dir, exist_ok=True)
        
        # Save to a dated news file in the output directory
        date_str = current_time.strftime('%Y-%m-%d')
        news_file = os.path.join(news_output_dir, f'news_{date_str}.txt')
        
        with open(news_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"News Update - {current_time}\n")
            f.write(f"{'='*50}\n\n")
            f.write(news + "\n\n")
        
        logger.info(f"Successfully saved news to {news_file}")
        print(f"News has been saved to: {os.path.abspath(news_file)}")
        
    except Exception as e:
        error_msg = f"Error in run_daily_agent: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"Error: {error_msg}")

def start_scheduler() -> None:
    """Initialize and start the scheduler."""
    logger.info("Starting news agent scheduler")
    
    # Schedule the job to run daily at the specified time
    schedule.every().day.at(SCHEDULE_TIME.strftime('%H:%M')).do(run_daily_agent)
    
    # Run immediately on startup
    logger.info("Running initial news check...")
    run_daily_agent()
    
    logger.info(f"Scheduler started. Next run at {SCHEDULE_TIME.strftime('%H:%M')} {TARGET_TIMEZONE.zone} time")
    
    try:
        while True:
            schedule.run_pending()
            time_until_next = schedule.idle_seconds()
            if time_until_next is not None and time_until_next > 0:
                logger.debug(f"Next run in {time_until_next/60:.1f} minutes")
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.critical(f"Scheduler crashed: {e}", exc_info=True)
        raise