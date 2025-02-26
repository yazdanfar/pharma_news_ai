"""
Main agent module for pharma_news_ai.
"""

import os
import time
import logging
import pandas as pd
from datetime import datetime

from .news_fetcher import NewsFetcher
from .content_processor import ContentProcessor
from .post_generator import PostGenerator
from .social_poster import SocialPoster
from .utils import save_posts_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PharmaNewsAgent:
    """
    Agent for pharmaceutical news aggregation and social media content generation.
    """
    
    def __init__(
        self,
        rss_feeds=None,
        data_dir='data',
        summarizer_model="facebook/bart-large-cnn",
        text_generator_model="EleutherAI/gpt-neo-1.3B",
        social_credentials=None
    ):
        """
        Initialize the PharmaNewsAgent.
        
        Args:
            rss_feeds (list, optional): List of RSS feed URLs for pharmaceutical news.
            data_dir (str): Directory to store data.
            summarizer_model (str): Hugging Face model for summarization.
            text_generator_model (str): Hugging Face model for text generation.
            social_credentials (dict, optional): Credentials for social media platforms.
        """
        # Create components
        self.news_fetcher = NewsFetcher(rss_feeds, data_dir)
        self.content_processor = ContentProcessor(summarizer_model)
        self.post_generator = PostGenerator(text_generator_model)
        self.social_poster = SocialPoster(social_credentials)
        
        self.data_dir = data_dir
        
        logger.info("PharmaNewsAgent initialized")
    
    def fetch_news(self, max_articles=10):
        """
        Fetch pharmaceutical news.
        
        Args:
            max_articles (int): Maximum number of articles to fetch.
            
        Returns:
            list: List of article dictionaries.
        """
        logger.info(f"Fetching up to {max_articles} articles...")
        return self.news_fetcher.fetch_articles(max_articles)
    
    def process_articles(self, articles):
        """
        Process articles to generate summaries.
        
        Args:
            articles (list): List of article dictionaries.
            
        Returns:
            list: List of processed article dictionaries.
        """
        logger.info(f"Processing {len(articles)} articles...")
        
        processed_articles = []
        for article in articles:
            try:
                if 'content' in article and article['content'].strip():
                    article['summary'] = self.content_processor.generate_summary(article['content'])
                else:
                    article['summary'] = article.get('title', '')
                processed_articles.append(article)
            except Exception as e:
                logger.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")
        
        return processed_articles
    
    def generate_posts(self, articles):
        """
        Generate social media posts for articles.
        
        Args:
            articles (list): List of article dictionaries.
            
        Returns:
            list: List of post data dictionaries.
        """
        logger.info(f"Generating posts for {len(articles)} articles...")
        
        posts_data = []
        for article in articles:
            try:
                summary = article.get('summary', '')
                posts = self.post_generator.generate_social_posts(article, summary)
                
                posts_data.append({
                    'article_title': article.get('title', ''),
                    'article_link': article.get('link', ''),
                    'article_source': article.get('source', ''),
                    'article_published': article.get('published', ''),
                    'linkedin_post': posts.get('linkedin', ''),
                    'facebook_post': posts.get('facebook', ''),
                    'twitter_post': posts.get('twitter', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                logger.error(f"Error generating posts for article {article.get('title', 'Unknown')}: {e}")
        
        # Save posts to CSV
        save_posts_to_csv(posts_data, self.data_dir)
        
        return posts_data
    
    def post_to_social(self, posts_data, platforms=None):
        """
        Post content to social media platforms.
        
        Args:
            posts_data (list): List of post data dictionaries.
            platforms (list, optional): List of platforms to post to.
            
        Returns:
            list: List of status dictionaries.
        """
        logger.info(f"Posting {len(posts_data)} articles to social media...")
        
        results = []
        
        for post_data in posts_data:
            posts = {
                'linkedin': post_data.get('linkedin_post', ''),
                'facebook': post_data.get('facebook_post', ''),
                'twitter': post_data.get('twitter_post', '')
            }
            
            status = self.social_poster.post_to_platforms(posts, platforms)
            
            results.append({
                'article_title': post_data.get('article_title', ''),
                'status': status
            })
        
        return results
    
    def run_once(self, max_articles=10, post_to_social=False, platforms=None):
        """
        Run the agent once.
        
        Args:
            max_articles (int): Maximum number of articles to fetch.
            post_to_social (bool): Whether to post to social media.
            platforms (list, optional): List of platforms to post to.
            
        Returns:
            tuple: Tuple of (articles, posts_data, posting_results).
        """
        logger.info("Starting agent run...")
        
        # Fetch and process articles
        articles = self.fetch_news(max_articles)
        processed_articles = self.process_articles(articles)
        
        # Generate posts
        posts_data = self.generate_posts(processed_articles)
        
        # Post to social media if requested
        posting_results = None
        if post_to_social:
            posting_results = self.post_to_social(posts_data, platforms)
        
        logger.info("Agent run completed")
        
        return articles, posts_data, posting_results
    
    def run(self, interval_hours=24, max_articles=10, post_to_social=False, platforms=None):
        """
        Run the agent continuously at specified intervals.
        
        Args:
            interval_hours (float): Interval between runs in hours.
            max_articles (int): Maximum number of articles to fetch per run.
            post_to_social (bool): Whether to post to social media.
            platforms (list, optional): List of platforms to post to.
        """
        logger.info(f"Starting continuous agent with {interval_hours} hour interval...")
        
        try:
            while True:
                start_time = time.time()
                
                try:
                    self.run_once(max_articles, post_to_social, platforms)
                except Exception as e:
                    logger.error(f"Error in agent run: {e}")
                
                # Calculate sleep time (accounting for time taken to run)
                elapsed = time.time() - start_time
                sleep_seconds = max(0, interval_hours * 3600 - elapsed)
                
                logger.info(f"Sleeping for {sleep_seconds / 3600:.2f} hours...")
                time.sleep(sleep_seconds)
        
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
        
        logger.info("Agent terminated")