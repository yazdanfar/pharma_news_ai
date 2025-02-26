"""
Utility functions for pharma_news_ai.
"""

import os
import csv
import json
import time
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_posts_to_csv(posts_data, data_dir='data', filename=None):
    """
    Save generated posts to a CSV file.
    
    Args:
        posts_data (list): List of dictionaries containing post data.
        data_dir (str): Directory to store data.
        filename (str, optional): Filename to use. If None, a timestamped filename will be generated.
        
    Returns:
        str: Path to the saved CSV file.
    """
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'social_posts_{timestamp}.csv'
    
    filepath = os.path.join(data_dir, filename)
    
    # Get all field names from all dictionaries
    fieldnames = set()
    for post_data in posts_data:
        fieldnames.update(post_data.keys())
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(posts_data)
    
    logger.info(f"Saved {len(posts_data)} posts to {filepath}")
    return filepath

def load_json_file(filepath):
    """
    Load a JSON file.
    
    Args:
        filepath (str): Path to the JSON file.
        
    Returns:
        dict or list: Loaded JSON data.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {filepath}: {e}")
        return None

def save_json_file(data, filepath):
    """
    Save data to a JSON file.
    
    Args:
        data (dict or list): Data to save.
        filepath (str): Path to save the file.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {filepath}: {e}")
        return False

def retry_with_backoff(func, max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Retry a function with exponential backoff.
    
    Args:
        func (callable): Function to retry.
        max_retries (int): Maximum number of retries.
        initial_delay (float): Initial delay in seconds.
        backoff_factor (float): Factor to multiply delay by after each retry.
        
    Returns:
        Any: Result of the function if successful.
        
    Raises:
        Exception: The last exception raised by the function.
    """
    retries = 0
    delay = initial_delay
    
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Max retries ({max_retries}) reached. Final error: {e}")
                raise
            
            # Add some randomness to the delay (jitter)
            jitter = random.uniform(0.8, 1.2)
            sleep_time = delay * jitter
            
            logger.warning(f"Attempt {retries} failed: {e}. Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
            
            # Increase delay for next retry
            delay *= backoff_factor

def extract_keywords(text, num_keywords=5):
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text (str): Text to extract keywords from.
        num_keywords (int): Number of keywords to extract.
        
    Returns:
        list: List of keywords.
    """
    # Common English stop words to ignore
    stop_words = set([
        'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
        'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'of', 'from',
        'that', 'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
        'he', 'she', 'his', 'her', 'we', 'our', 'you', 'your', 'has', 'have',
        'had', 'been', 'would', 'could', 'should', 'will', 'may', 'can', 'be',
        'as', 'if', 'than', 'when', 'what', 'who', 'how', 'why', 'where', 'which'
    ])
    
    # Clean text and split into words
    words = text.lower()
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in words)
    words = words.split()
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        if word not in stop_words and len(word) > 3:  # Only consider words longer than 3 chars
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    return [word for word, count in sorted_words[:num_keywords]]