"""
Example script to run the PharmaNewsAgent.
"""

import argparse
import json
import os
import logging
from pharma_news_ai import PharmaNewsAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the PharmaNewsAgent')
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously at specified intervals'
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=24,
        help='Interval between runs in hours (default: 24)'
    )
    
    parser.add_argument(
        '--max-articles',
        type=int,
        default=10,
        help='Maximum number of articles to fetch per run (default: 10)'
    )
    
    parser.add_argument(
        '--post-to-social',
        action='store_true',
        help='Post to social media'
    )
    
    parser.add_argument(
        '--platforms',
        nargs='+',
        choices=['linkedin', 'facebook', 'twitter'],
        default=None,
        help='Platforms to post to (default: all configured platforms)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory to store data (default: data)'
    )
    
    parser.add_argument(
        '--summarizer-model',
        type=str,
        default="facebook/bart-large-cnn",
        help='Hugging Face model for summarization (default: facebook/bart-large-cnn)'
    )
    
    parser.add_argument(
        '--text-generator-model',
        type=str,
        default="EleutherAI/gpt-neo-1.3B",
        help='Hugging Face model for text generation (default: EleutherAI/gpt-neo-1.3B)'
    )
    
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from file."""
    if not config_path or not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def main():
    """Main function."""
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Get parameters from config or args
    rss_feeds = config.get('rss_feeds')
    data_dir = args.data_dir or config.get('data_dir', 'data')
    summarizer_model = args.summarizer_model or config.get('summarizer_model', "facebook/bart-large-cnn")
    text_generator_model = args.text_generator_model or config.get('text_generator_model', "EleutherAI/gpt-neo-1.3B")
    social_credentials = config.get('social_credentials')
    
    # Create the agent
    agent = PharmaNewsAgent(
        rss_feeds=rss_feeds,
        data_dir=data_dir,
        summarizer_model=summarizer_model,
        text_generator_model=text_generator_model,
        social_credentials=social_credentials
    )
    
    # Run the agent
    if args.continuous:
        logger.info(f"Running continuously with {args.interval} hour interval...")
        agent.run(
            interval_hours=args.interval,
            max_articles=args.max_articles,
            post_to_social=args.post_to_social,
            platforms=args.platforms
        )
    else:
        logger.info("Running once...")
        articles, posts_data, posting_results = agent.run_once(
            max_articles=args.max_articles,
            post_to_social=args.post_to_social,
            platforms=args.platforms
        )
        
        # Print summary
        logger.info(f"Fetched {len(articles)} articles")
        logger.info(f"Generated {len(posts_data)} sets of social media posts")
        
        if posting_results:
            success_count = sum(1 for result in posting_results if all(
                status.get('status') in ('success', 'simulated') 
                for platform, status in result['status'].items()
            ))
            logger.info(f"Successfully posted {success_count}/{len(posting_results)} articles")

if __name__ == '__main__':
    main()