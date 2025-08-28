#!/usr/bin/env python3
"""
RSS Feed Parser

This script reads RSS feed URLs from sources.txt, parses each feed,
and extracts article information including title, URL, publishing date, and content.
Includes duplicate detection and occurrence tracking.
"""

import feedparser
import requests
from datetime import datetime
import time
from urllib.parse import urlparse
import sys
from typing import List, Dict, Optional, Set
import logging
from difflib import SequenceMatcher
import hashlib
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RSSParser:
    def __init__(self, sources_file: str = "sources.txt"):
        self.sources_file = sources_file
        self.feeds = []
        self.articles = []
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        self.article_occurrences: Dict[str, int] = defaultdict(int)
        self.article_mapping: Dict[str, Dict] = {}
        
    def load_sources(self) -> List[str]:
        """Load RSS feed URLs from sources.txt file."""
        try:
            with open(self.sources_file, 'r') as file:
                feeds = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            logger.info(f"Loaded {len(feeds)} RSS feed URLs from {self.sources_file}")
            return feeds
        except FileNotFoundError:
            logger.error(f"Sources file '{self.sources_file}' not found")
            return []
        except Exception as e:
            logger.error(f"Error loading sources: {e}")
            return []
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for better duplicate detection."""
        if not url:
            return ""
        
        # Remove common tracking parameters
        url = url.split('?')[0] if '?' in url else url
        url = url.split('#')[0] if '#' in url else url
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        return url.lower()
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for better duplicate detection."""
        if not title:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        title = title.lower().strip()
        
        # Remove common prefixes/suffixes that don't affect uniqueness
        title = title.replace('breaking:', '').replace('breaking news:', '')
        title = title.replace('exclusive:', '').replace('exclusive news:', '')
        
        return title
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate a hash of the content for duplicate detection."""
        if not content:
            return ""
        
        # Normalize content for better hash comparison
        normalized = content.lower().strip()
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def is_similar_title(self, title1: str, title2: str, threshold: float = 0.85) -> bool:
        """Check if two titles are similar using fuzzy matching."""
        if not title1 or not title2:
            return False
        
        # Normalize titles
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)
        
        # Exact match after normalization
        if norm1 == norm2:
            return True
        
        # Fuzzy matching using SequenceMatcher
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        return similarity >= threshold
    
    def get_article_key(self, article: Dict) -> str:
        """Get a unique key for an article based on URL, title, or content."""
        url = self.normalize_url(article.get('url', ''))
        title = self.normalize_title(article.get('title', ''))
        content_hash = self.calculate_content_hash(article.get('content', ''))
        
        # Prefer URL as the key, fall back to title, then content hash
        if url:
            return f"url:{url}"
        elif title:
            return f"title:{title}"
        elif content_hash:
            return f"content:{content_hash}"
        else:
            return f"fallback:{hash(str(article))}"
    
    def is_duplicate_article(self, article: Dict) -> bool:
        """Check if an article is a duplicate and track occurrences."""
        url = self.normalize_url(article.get('url', ''))
        title = article.get('title', '')
        content = article.get('content', '')
        content_hash = self.calculate_content_hash(content)
        
        # Check URL duplicates
        if url and url in self.seen_urls:
            logger.debug(f"Duplicate detected by URL: {url}")
            self.track_occurrence(article, "url")
            return True
        
        # Check title duplicates (exact match after normalization)
        normalized_title = self.normalize_title(title)
        if normalized_title and normalized_title in self.seen_titles:
            logger.debug(f"Duplicate detected by title: {title}")
            self.track_occurrence(article, "title")
            return True
        
        # Check content duplicates
        if content_hash and content_hash in self.seen_content_hashes:
            logger.debug(f"Duplicate detected by content hash")
            self.track_occurrence(article, "content")
            return True
        
        # Check for similar titles (fuzzy matching)
        for seen_title in self.seen_titles:
            if self.is_similar_title(title, seen_title):
                logger.debug(f"Duplicate detected by similar title: '{title}' vs '{seen_title}'")
                self.track_occurrence(article, "similar_title")
                return True
        
        # If not a duplicate, add to seen sets and track as new occurrence
        if url:
            self.seen_urls.add(url)
        if normalized_title:
            self.seen_titles.add(normalized_title)
        if content_hash:
            self.seen_content_hashes.add(content_hash)
        
        # Track this as a new occurrence
        self.track_occurrence(article, "new")
        return False
    
    def track_occurrence(self, article: Dict, detection_method: str):
        """Track the occurrence of an article."""
        article_key = self.get_article_key(article)
        self.article_occurrences[article_key] += 1
        
        # Store the article data if this is the first occurrence
        if article_key not in self.article_mapping:
            self.article_mapping[article_key] = article.copy()
            # Add occurrence count to the article data
            self.article_mapping[article_key]['occurrences'] = 1
        else:
            # Update occurrence count
            self.article_mapping[article_key]['occurrences'] = self.article_occurrences[article_key]
    
    def parse_feed(self, feed_url: str) -> Optional[Dict]:
        """Parse a single RSS feed and return feed information."""
        try:
            logger.info(f"Parsing feed: {feed_url}")
            
            # Add timeout and headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Parse the feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issues for {feed_url}: {feed.bozo_exception}")
            
            feed_info = {
                'url': feed_url,
                'title': getattr(feed.feed, 'title', 'Unknown'),
                'description': getattr(feed.feed, 'description', ''),
                'entries': []
            }
            
            for entry in feed.entries:
                article = self.extract_article_info(entry)
                if article:
                    feed_info['entries'].append(article)
            
            logger.info(f"Found {len(feed_info['entries'])} articles in {feed_url}")
            return feed_info
            
        except Exception as e:
            logger.error(f"Error parsing feed {feed_url}: {e}")
            return None
    
    def extract_article_info(self, entry) -> Optional[Dict]:
        """Extract article information from a feed entry."""
        try:
            # Extract title
            title = getattr(entry, 'title', 'No title available')
            
            # Extract URL
            url = getattr(entry, 'link', '')
            
            # Extract publishing date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime(*entry.updated_parsed[:6])
            else:
                published_date = datetime.now()
            
            # Extract content
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
            
            # Clean content (remove HTML tags if present)
            content = self.clean_content(content)
            
            return {
                'title': title,
                'url': url,
                'published_date': published_date,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"Error extracting article info: {e}")
            return None
    
    def clean_content(self, content: str) -> str:
        """Clean HTML content and extract plain text."""
        import re
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Decode HTML entities
        import html
        content = html.unescape(content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def parse_all_feeds(self) -> List[Dict]:
        """Parse all RSS feeds and return article information with duplicate removal and occurrence tracking."""
        feed_urls = self.load_sources()
        
        if not feed_urls:
            logger.error("No feed URLs found")
            return []
        
        total_articles_found = 0
        duplicates_removed = 0
        
        for i, feed_url in enumerate(feed_urls, 1):
            logger.info(f"Processing feed {i}/{len(feed_urls)}: {feed_url}")
            
            feed_info = self.parse_feed(feed_url)
            if feed_info:
                for article in feed_info['entries']:
                    total_articles_found += 1
                    if self.is_duplicate_article(article):
                        duplicates_removed += 1
            
            # Add a small delay to be respectful to servers
            time.sleep(1)
        
        # Convert the article mapping to a list and sort by publication date (newest first)
        all_articles = list(self.article_mapping.values())
        all_articles.sort(key=lambda x: x['published_date'], reverse=True)
        
        logger.info(f"Total articles found: {total_articles_found}")
        logger.info(f"Duplicates removed: {duplicates_removed}")
        logger.info(f"Unique articles: {len(all_articles)}")
        
        # Log occurrence statistics
        occurrence_stats = defaultdict(int)
        for article in all_articles:
            occurrence_stats[article['occurrences']] += 1
        
        logger.info("Occurrence statistics:")
        for occurrences, count in sorted(occurrence_stats.items()):
            logger.info(f"  {occurrences} occurrence(s): {count} articles")
        
        return all_articles
    
    def save_to_file(self, articles: List[Dict], output_file: str = "articles_summary.txt"):
        """Save articles summary to a text file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write("RSS FEED ARTICLES SUMMARY (DUPLICATES REMOVED)\n")
                file.write("=" * 70 + "\n\n")
                file.write(f"Total unique articles: {len(articles)}\n")
                file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Add occurrence statistics
                occurrence_stats = defaultdict(int)
                for article in articles:
                    occurrence_stats[article['occurrences']] += 1
                
                file.write("Occurrence Statistics:\n")
                for occurrences, count in sorted(occurrence_stats.items()):
                    file.write(f"  {occurrences} occurrence(s): {count} articles\n")
                file.write("\n" + "=" * 70 + "\n\n")
                
                for i, article in enumerate(articles, 1):
                    file.write(f"Article {i}\n")
                    file.write("-" * 30 + "\n")
                    file.write(f"Title: {article['title']}\n")
                    file.write(f"URL: {article['url']}\n")
                    file.write(f"Published: {article['published_date'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write(f"Occurrences: {article['occurrences']}\n")
                    file.write(f"Content: {article['content'][:500]}...\n" if len(article['content']) > 500 else f"Content: {article['content']}\n")
                    file.write("\n" + "=" * 70 + "\n\n")
            
            logger.info(f"Articles summary saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
    
    def print_summary(self, articles: List[Dict]):
        """Print a summary of all articles to console."""
        print(f"\n{'='*90}")
        print(f"RSS FEED ARTICLES SUMMARY - {len(articles)} Unique Articles Found")
        print(f"{'='*90}\n")
        
        # Print occurrence statistics
        occurrence_stats = defaultdict(int)
        for article in articles:
            occurrence_stats[article['occurrences']] += 1
        
        print("Occurrence Statistics:")
        for occurrences, count in sorted(occurrence_stats.items()):
            print(f"  {occurrences} occurrence(s): {count} articles")
        print()
        
        for i, article in enumerate(articles, 1):
            print(f"Article {i}")
            print(f"Title: {article['title']}")
            print(f"URL: {article['url']}")
            print(f"Published: {article['published_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Occurrences: {article['occurrences']}")
            print(f"Content Preview: {article['content'][:200]}...")
            print("-" * 90)
            print()

def main():
    """Main function to run the RSS parser."""
    parser = RSSParser()
    
    print("Starting RSS feed parsing with duplicate detection and occurrence tracking...")
    articles = parser.parse_all_feeds()
    
    if articles:
        # Print summary to console
        parser.print_summary(articles)
        
        # Save to file
        parser.save_to_file(articles)
        
        print(f"\nProcessing complete! Found {len(articles)} unique articles.")
        print("Summary saved to 'articles_summary.txt'")
    else:
        print("No articles found. Please check your RSS feed URLs.")

if __name__ == "__main__":
    main()
