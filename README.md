# PharmaNewsAI

An open-source AI agent for pharmaceutical news aggregation and social media content generation. This package helps you automatically:

1. **Collect** pharmaceutical news from multiple RSS feeds
2. **Analyze** and summarize the content
3. **Generate** platform-specific posts for LinkedIn, Facebook, and Twitter
4. **Store** the results for review or publishing

## Features

- **Automated News Collection**: Fetches pharmaceutical news from multiple sources
- **Content Summarization**: Uses NLP to create concise summaries of articles
- **Platform-Optimized Content**: Creates tailored content for each social platform
- **Flexible Scheduling**: Run once or continuously at specified intervals
- **Local Storage**: All data is stored locally with no cloud dependencies
- **Open-Source Stack**: Built entirely with free, open-source libraries

## Installation

### From GitHub

```bash
git clone https://github.com/yourusername/pharma_news_ai.git
cd pharma_news_ai
pip install -e .
```

### Requirements

- Python 3.7 or higher
- Dependencies listed in `requirements.txt`

## Quick Start

### Basic Usage

```python
from pharma_news_ai import PharmaNewsAgent

# Create the agent
agent = PharmaNewsAgent()

# Run once
articles, posts, results = agent.run_once(max_articles=5)

# Print generated LinkedIn post for the first article
print(posts[0]['linkedin_post'])
```

### Command Line

```bash
# Run once
pharma-news-ai --max-articles 5

# Run continuously every 12 hours
pharma-news-ai --continuous --interval 12 --max-articles 10
```

## Configuration

### Custom RSS Feeds

You can provide your own list of pharmaceutical RSS feeds:

```python
feeds = [
    'https://www.fiercepharma.com/rss/xml',
    'https://www.biopharmadive.com/feeds/news/',
    'https://www.your-pharma-site.com/feed/',
]

agent = PharmaNewsAgent(rss_feeds=feeds)
```

### Using Smaller Models

For faster performance or lower resource usage:

```python
agent = PharmaNewsAgent(
    summarizer_model="distilbart-cnn-6-6",
    text_generator_model="distilgpt2"
)
```

### Configuration File

You can also use a JSON configuration file:

```json
{
    "rss_feeds": [
        "https://www.fiercepharma.com/rss/xml",
        "https://www.biopharmadive.com/feeds/news/"
    ],
    "data_dir": "my_data",
    "summarizer_model": "facebook/bart-large-cnn",
    "text_generator_model": "EleutherAI/gpt-neo-1.3B",
    "social_credentials": {
        "linkedin": {
            "username": "your_username",
            "password": "your_password"
        }
    }
}
```

Then use:

```bash
pharma-news-ai --config my_config.json
```

## Components

The package is divided into several modules:

- **NewsFetcher**: Retrieves articles from RSS feeds
- **ContentProcessor**: Summarizes and processes article content
- **PostGenerator**: Creates platform-specific social media posts
- **SocialPoster**: Handles posting to social media platforms
- **PharmaNewsAgent**: Orchestrates the entire workflow

## Social Media Posting

By default, posts are generated but not published to social platforms. To enable actual posting:

1. Install platform-specific libraries:
   ```bash
   pip install linkedin-api facebook-sdk tweepy
   ```

2. Create a credentials file with your API keys/tokens:
   ```json
   {
       "linkedin": {
           "username": "your_username",
           "password": "your_password"
       },
       "facebook": {
           "access_token": "your_access_token"
       },
       "twitter": {
           "consumer_key": "your_consumer_key",
           "consumer_secret": "your_consumer_secret",
           "access_token": "your_access_token",
           "access_token_secret": "your_access_token_secret"
       }
   }
   ```

3. Provide these credentials when creating the agent:
   ```python
   import json
   
   with open('social_credentials.json', 'r') as f:
       credentials = json.load(f)
       
   agent = PharmaNewsAgent(social_credentials=credentials)
   ```

4. Enable posting when running the agent:
   ```python
   agent.run_once(post_to_social=True)
   ```

## Resource Management

The Hugging Face models used for text generation and summarization can require significant resources. Some tips for management:

- Use `distilbart-cnn-6-6` instead of `facebook/bart-large-cnn` for summarization
- Use `distilgpt2` instead of `EleutherAI/gpt-neo-1.3B` for text generation
- Run on a machine with at least 4GB RAM
- First run will download models (~4GB total)

## Output Example

Generated LinkedIn post:
```
📊 Exciting developments at Pfizer! Their new antimicrobial research initiative shows promising results in early-stage trials.

This could represent a significant step forward in addressing antibiotic resistance, one of healthcare's most pressing challenges.

What are your thoughts on pharmaceutical companies increasing investment in antimicrobial research? Is this the breakthrough we've been waiting for?

#Pharma #Healthcare #AntibioticResistance

Read more: https://www.fiercepharma.com/article/12345
```

## Extending the Package

### Adding New Social Platforms

You can extend the `SocialPoster` class to support additional platforms:

```python
from pharma_news_ai.social_poster import SocialPoster

class ExtendedSocialPoster(SocialPoster):
    def __init__(self, credentials=None):
        super().__init__(credentials)
        # Add your platform to the list if credentials exist
        if 'instagram' in self.credentials:
            self.platforms.append('instagram')
    
    def _post_to_instagram(self, text):
        # Implementation for Instagram posting
        pass
```

### Custom Post Templates

Modify the `PostGenerator` class to create customized templates:

```python
from pharma_news_ai.post_generator import PostGenerator

class CustomPostGenerator(PostGenerator):
    def _generate_linkedin_post(self, title, content_snippet, link):
        # Your custom LinkedIn post format
        return f"INDUSTRY ALERT: {title}\n\n{content_snippet}\n\n{link}"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.