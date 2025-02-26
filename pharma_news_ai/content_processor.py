"""
Content processing module for pharma_news_ai.
"""

import re
import numpy as np
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from transformers import pipeline
import nltk
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    logger.info("Downloading NLTK stopwords...")
    nltk.download('stopwords')

class ContentProcessor:
    """Process and summarize news article content."""
    
    def __init__(self, summarizer_model="facebook/bart-large-cnn"):
        """
        Initialize the ContentProcessor.
        
        Args:
            summarizer_model (str): Hugging Face model to use for summarization.
        """
        logger.info(f"Initializing summarizer with model: {summarizer_model}")
        self.summarizer = pipeline("summarization", model=summarizer_model)
        self.stop_words = set(stopwords.words('english'))
    
    def generate_summary(self, text, max_length=150, min_length=50):
        """
        Generate a summary of the given text.
        
        Args:
            text (str): Text to summarize.
            max_length (int): Maximum length of the summary in words.
            min_length (int): Minimum length of the summary in words.
            
        Returns:
            str: Generated summary.
        """
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If text is too short, return it as is
        if len(text.split()) < min_length:
            return text
            
        # Try using the summarizer
        try:
            # Split into chunks if text is too long (BART has a limit)
            max_chunk_length = 1024
            chunks = self._split_into_chunks(text, max_chunk_length)
                
            # Summarize each chunk
            summaries = []
            for chunk in chunks:
                summary = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                summaries.append(summary[0]['summary_text'])
                
            # Combine summaries
            final_summary = ' '.join(summaries)
            
            # Ensure it's not too long
            if len(final_summary.split()) > max_length:
                final_summary = ' '.join(final_summary.split()[:max_length])
                
            return final_summary
            
        except Exception as e:
            logger.warning(f"Error in summarization: {e}")
            # If summarization fails, extract key sentences
            return self.extract_key_sentences(text, 3)
    
    def _split_into_chunks(self, text, max_chunk_length):
        """
        Split text into chunks of maximum length.
        
        Args:
            text (str): Text to split.
            max_chunk_length (int): Maximum chunk length in words.
            
        Returns:
            list: List of text chunks.
        """
        chunks = []
        sentences = sent_tokenize(text)
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            words = len(sentence.split())
            if current_length + words <= max_chunk_length:
                current_chunk.append(sentence)
                current_length += words
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = words
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks
    
    def extract_key_sentences(self, text, num_sentences=3):
        """
        Extract key sentences using a TextRank-inspired algorithm.
        
        Args:
            text (str): Text to extract sentences from.
            num_sentences (int): Number of key sentences to extract.
            
        Returns:
            str: String of key sentences.
        """
        sentences = sent_tokenize(text)
        
        # If there are fewer sentences than requested, return all
        if len(sentences) <= num_sentences:
            return ' '.join(sentences)
            
        # Create sentence similarity matrix
        sentence_similarity_matrix = np.zeros((len(sentences), len(sentences)))
        
        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i != j:
                    sentence_similarity_matrix[i][j] = self._sentence_similarity(sentences[i], sentences[j])
                    
        # Use PageRank-like algorithm to get sentence scores
        sentence_scores = np.array([sum(row) for row in sentence_similarity_matrix])
        
        # Get top sentences
        ranked_indices = np.argsort(sentence_scores)[-num_sentences:]
        ranked_indices = sorted(ranked_indices)
        
        return ' '.join([sentences[i] for i in ranked_indices])
    
    def _sentence_similarity(self, sent1, sent2):
        """
        Calculate cosine similarity between two sentences.
        
        Args:
            sent1 (str): First sentence.
            sent2 (str): Second sentence.
            
        Returns:
            float: Similarity score between 0 and 1.
        """
        words1 = [word.lower() for word in sent1.split() if word.lower() not in self.stop_words]
        words2 = [word.lower() for word in sent2.split() if word.lower() not in self.stop_words]
        
        # If either sentence has no meaningful words, return 0
        if not words1 or not words2:
            return 0
        
        # Create word vectors
        all_words = list(set(words1 + words2))
        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)
        
        # Fill the vectors
        for word in words1:
            vector1[all_words.index(word)] += 1
                
        for word in words2:
            vector2[all_words.index(word)] += 1
                
        # Calculate cosine similarity
        return 1 - cosine_distance(vector1, vector2)