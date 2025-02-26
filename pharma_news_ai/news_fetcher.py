"""
News fetching module for pharma_news_ai.
"""

import os
import json
import time
import random
import feedparser
from datetime import datetime
from newspaper import Article
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    """Fetch pharmaceutical news from various RSS feeds."""
    
    def __init__(self, rss_feeds=None, data_dir='data'):
        """
        Initialize the NewsFetcher.
        
        Args:
            rss_feeds (list): List of RSS feed URLs for pharmaceutical news.
            data_dir (str): Directory to store data.
        """
        self.rss_feeds = rss_feeds or [
            'https://www.fiercepharma.com/rss/xml',
            'https://www.biopharmadive.com/feeds/news/',
            'https://www.pharmaceutical-technology.com/feed/',
            'https://www.drugdiscoverytrends.com/feed/',
            'https://www.pharmtech.com/feed',
        ]
        
        self.data_dir = data_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
    
    def fetch_articles(self, max_articles=10, save=True):
        """
        Fetch articles from RSS feeds.
        
        Args:
            max_articles (int): Maximum number of articles to fetch.
            save (bool): Whether to save the articles to a file.
            
        Returns:
            list: List of article dictionaries.
        """
        all_articles = []
        articles_per_feed = max(1, max_articles // len(self.rss_feeds))
        
        logger.info(f"Fetching up to {max_articles} articles from {len(self.rss_feeds)} feeds...")
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Parsing feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:articles_per_feed]:
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.get('published', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        'source': feed.feed.title
                    }
                    
                    # Get full article content using newspaper3k
                    try:
                        logger.info(f"Downloading article: {entry.title}")
                        news_article = Article(entry.link)
                        news_article.download()
                        # Add a small delay to avoid overloading servers
                        time.sleep(random.uniform(1.0, 3.0))
                        news_article.parse()
                        article['content'] = news_article.text
                        
                        # Try to get image if available
                        if news_article.top_image:
                            article['image_url'] = news_article.top_image
                    except Exception as e:
                        logger.warning(f"Error downloading article content: {e}")
                        article['content'] = entry.get('summary', '')
                    
                    all_articles.append(article)
            except Exception as e:
                logger.error(f"Error parsing feed {feed_url}: {e}")
        
        if save and all_articles:
            self._save_articles(all_articles)
            
        logger.info(f"Fetched {len(all_articles)} articles.")
        return all_articles
    
    def _save_articles(self, articles):
        """
        Save articles to a JSON file.
        
        Args:
            articles (list): List of article dictionaries.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(self.data_dir, f'articles_{timestamp}.json')
        
        with open(filename, 'w') as f:
            json.dump(articles, f, indent=4)
            
        logger.info(f"Saved {len(articles)} articles to {filename}")