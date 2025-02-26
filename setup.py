from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pharma_news_ai",
    version="0.1.0",
    author="Javad Yazdanfar",
    author_email="yazdanfar.de@gmail.com",
    description="AI agent for pharmaceutical news aggregation and social media content generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yazdanfar/pharma_news_ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Social Media",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "feedparser",
        "pandas",
        "numpy",
        "beautifulsoup4",
        "newspaper3k",
        "nltk",
        "transformers",
        "torch",
    ],
    entry_points={
        "console_scripts": [
            "pharma-news-ai=pharma_news_ai.examples.run_agent:main",
        ],
    },
)