"""
Social media post generator module for pharma_news_ai.
"""

import re
from transformers import pipeline
from nltk.tokenize import sent_tokenize
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostGenerator:
    """Generate social media posts from news articles."""
    
    def __init__(self, text_generator_model="EleutherAI/gpt-neo-1.3B"):
        """
        Initialize the PostGenerator.
        
        Args:
            text_generator_model (str): Hugging Face model to use for text generation.
        """
        logger.info(f"Initializing text generator with model: {text_generator_model}")
        self.text_generator = pipeline("text-generation", model=text_generator_model)
    
    def generate_social_posts(self, article, summary=None):
        """
        Generate social media posts for different platforms.
        
        Args:
            article (dict): Article dictionary containing title, link, etc.
            summary (str, optional): Pre-generated summary of the article.
            
        Returns:
            dict: Dictionary containing posts for different platforms.
        """
        title = article['title']
        link = article['link']
        
        # Use provided summary or get snippet from content
        if not summary and 'content' in article:
            content_snippet = self._get_snippet(article['content'], 100)
        else:
            content_snippet = summary or title
        
        logger.info(f"Generating social media posts for: {title}")
        
        # LinkedIn post (more professional and detailed)
        linkedin_post = self._generate_linkedin_post(title, content_snippet, link)
        
        # Facebook post (more conversational)
        facebook_post = self._generate_facebook_post(title, content_snippet, link)
        
        # Twitter post (concise)
        twitter_post = self._generate_twitter_post(title, link)
        
        return {
            'linkedin': linkedin_post,
            'facebook': facebook_post,
            'twitter': twitter_post
        }
    
    def _generate_linkedin_post(self, title, content_snippet, link):
        """
        Generate a LinkedIn post.
        
        Args:
            title (str): Article title.
            content_snippet (str): Article content snippet.
            link (str): Article link.
            
        Returns:
            str: LinkedIn post.
        """
        try:
            prompt = f"Write a professional LinkedIn post about this pharmaceutical news: {title}. Include a brief summary and ask for opinions."
            generated = self.text_generator(prompt, max_length=200, do_sample=True, temperature=0.7)[0]['generated_text']
            post = self._clean_generated_text(prompt, generated)
            
            # Add hashtags
            hashtags = self._generate_hashtags(title, content_snippet, 3)
            
            return f"{post}\n\n{hashtags}\n\nRead more: {link}"
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {e}")
            return f"📊 Pharmaceutical Update: {title}\n\nInteresting development in the pharma sector. What are your thoughts on this?\n\nRead more: {link}"
    
    def _generate_facebook_post(self, title, content_snippet, link):
        """
        Generate a Facebook post.
        
        Args:
            title (str): Article title.
            content_snippet (str): Article content snippet.
            link (str): Article link.
            
        Returns:
            str: Facebook post.
        """
        try:
            prompt = f"Write a conversational Facebook post about this pharmaceutical news: {title}. Keep it engaging but informative."
            generated = self.text_generator(prompt, max_length=150, do_sample=True, temperature=0.7)[0]['generated_text']
            post = self._clean_generated_text(prompt, generated)
            
            return f"{post}\n\nRead more: {link}"
        except Exception as e:
            logger.error(f"Error generating Facebook post: {e}")
            return f"💊 Just came across this interesting pharma news: {title}\n\nThoughts? 🤔\n\nRead more: {link}"
    
    def _generate_twitter_post(self, title, link):
        """
        Generate a Twitter post (X post).
        
        Args:
            title (str): Article title.
            link (str): Article link.
            
        Returns:
            str: Twitter post.
        """
        try:
            prompt = f"Write a concise tweet about this pharmaceutical news in less than 280 characters: {title}"
            generated = self.text_generator(prompt, max_length=100, do_sample=True, temperature=0.7)[0]['generated_text']
            post = self._clean_generated_text(prompt, generated)
            
            # Make sure Twitter post is under 280 characters including the link
            if len(post) + len(link) + 1 > 280:
                post = post[:280 - len(link) - 4] + "..."
                
            # Add some hashtags if there's room
            hashtags = ""
            if len(post) + len(link) + 1 < 240:  # Leave room for hashtags
                hashtags = self._generate_hashtags(title, "", 2, short=True)
            
            return f"{post} {hashtags} {link}"
        except Exception as e:
            logger.error(f"Error generating Twitter post: {e}")
            # Fallback is a very simple tweet that's guaranteed to be short enough
            return f"New in pharma: {title[:100]}... {link}"
    
    def _clean_generated_text(self, prompt, generated_text):
        """
        Clean generated text by removing the prompt and other irrelevant parts.
        
        Args:
            prompt (str): The prompt used for generation.
            generated_text (str): The raw generated text.
            
        Returns:
            str: Cleaned text.
        """
        # Remove the prompt
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
            
        # Remove any quotation marks at the beginning and end
        generated_text = generated_text.strip('"')
        
        # Remove any "User:" or "AI:" or similar prefixes
        generated_text = re.sub(r'^(User:|AI:|Assistant:|Human:)', '', generated_text).strip()
        
        # Take only the first few sentences if the text is too long
        sentences = sent_tokenize(generated_text)
        if len(sentences) > 5:
            generated_text = ' '.join(sentences[:5])
            
        return generated_text
    
    def _get_snippet(self, content, max_words=100):
        """
        Get a snippet of the content.
        
        Args:
            content (str): The full content.
            max_words (int): Maximum number of words in the snippet.
            
        Returns:
            str: Content snippet.
        """
        words = content.split()
        if len(words) <= max_words:
            return content
        return ' '.join(words[:max_words]) + '...'
    
    def _generate_hashtags(self, title, content, num_hashtags=3, short=False):
        """
        Generate hashtags from title and content.
        
        Args:
            title (str): Article title.
            content (str): Article content.
            num_hashtags (int): Number of hashtags to generate.
            short (bool): Whether to generate short hashtags for platforms with character limits.
            
        Returns:
            str: String of hashtags.
        """
        # Common pharma industry hashtags
        common_hashtags = [
            'Pharma', 'Pharmaceutical', 'Healthcare', 'Medicine', 'BioTech', 
            'DrugDevelopment', 'ClinicalTrials', 'MedicalResearch', 'HealthTech',
            'LifeSciences', 'PharmaIndustry'
        ]
        
        # For short format, use shorter hashtags
        if short:
            common_hashtags = ['Pharma', 'Health', 'Med', 'Biotech', 'Science', 'Research']
        
        # Select random hashtags from the common list
        import random
        selected_hashtags = random.sample(common_hashtags, min(num_hashtags, len(common_hashtags)))
        
        # Format hashtags
        hashtag_string = ' '.join([f"#{tag}" for tag in selected_hashtags])
        
        return hashtag_string