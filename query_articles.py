#!/usr/bin/env python3
"""
Article Query Script

This script reads articles from articles_summary.txt and allows querying
articles by date range. It parses the articles and filters them based on
start and end dates provided as command line arguments.
"""

import argparse
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import sys
import os
from urllib.parse import urlparse
from collections import defaultdict, Counter

class ArticleQuery:
    def __init__(self, articles_file: str = "articles_summary.txt"):
        self.articles_file = articles_file
        self.articles = []
        
    def parse_articles_file(self) -> List[Dict]:
        """Parse the articles_summary.txt file and extract article information."""
        if not os.path.exists(self.articles_file):
            print(f"Error: Articles file '{self.articles_file}' not found.")
            return []
        
        articles = []
        current_article = {}
        
        try:
            with open(self.articles_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Look for article start pattern
                if line.startswith("Article ") and "------------------------------" in lines[i+1]:
                    # Save previous article if exists
                    if current_article:
                        articles.append(current_article)
                    
                    # Start new article
                    current_article = {}
                    article_num = line.split()[1]
                    current_article['number'] = int(article_num)
                    i += 2  # Skip the separator line
                    continue
                
                # Parse article fields
                if line.startswith("Title: "):
                    current_article['title'] = line[7:]
                elif line.startswith("URL: "):
                    current_article['url'] = line[5:]
                elif line.startswith("Published: "):
                    date_str = line[11:]
                    try:
                        current_article['published_date'] = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        print(f"Warning: Could not parse date '{date_str}' for article {current_article.get('number', 'unknown')}")
                        current_article['published_date'] = None
                elif line.startswith("Occurrences: "):
                    current_article['occurrences'] = int(line[13:])
                elif line.startswith("Content: "):
                    content = line[9:]
                    # Continue reading content if it spans multiple lines
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith("="):
                        content += " " + lines[j].strip()
                        j += 1
                    current_article['content'] = content
                    i = j - 1  # Adjust index
                
                i += 1
            
            # Add the last article
            if current_article:
                articles.append(current_article)
            
            print(f"Successfully parsed {len(articles)} articles from {self.articles_file}")
            return articles
            
        except Exception as e:
            print(f"Error parsing articles file: {e}")
            return []
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "unknown"
    
    def generate_metadata(self, articles: List[Dict], start_date: str, end_date: str) -> Dict:
        """Generate comprehensive metadata about the filtered articles."""
        if not articles:
            return {}
        
        # Basic statistics
        total_articles = len(articles)
        
        # Date range analysis
        dates = [article['published_date'].date() for article in articles if article.get('published_date')]
        date_range = f"{min(dates)} to {max(dates)}" if dates else "N/A"
        
        # Source domain analysis
        domains = [self.extract_domain(article['url']) for article in articles if article.get('url')]
        domain_counts = Counter(domains)
        unique_sources = len(domain_counts)
        
        # Top sources
        top_sources = domain_counts.most_common(5)
        
        # Occurrence analysis
        occurrence_counts = Counter([article['occurrences'] for article in articles])
        
        # Content length analysis
        content_lengths = [len(article.get('content', '')) for article in articles]
        avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        
        # Time distribution
        hour_distribution = defaultdict(int)
        for article in articles:
            if article.get('published_date'):
                hour = article['published_date'].hour
                hour_distribution[hour] += 1
        
        peak_hour = max(hour_distribution.items(), key=lambda x: x[1]) if hour_distribution else (0, 0)
        
        return {
            'query_date_range': f"{start_date} to {end_date}",
            'total_articles': total_articles,
            'actual_date_range': date_range,
            'unique_sources': unique_sources,
            'top_sources': top_sources,
            'occurrence_distribution': dict(occurrence_counts),
            'avg_content_length': int(avg_content_length),
            'peak_publishing_hour': f"{peak_hour[0]:02d}:00 ({peak_hour[1]} articles)",
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_file': self.articles_file
        }
    
    def filter_by_date_range(self, articles: List[Dict], start_date: str, end_date: str) -> List[Dict]:
        """Filter articles by date range."""
        try:
            # Parse date strings
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            filtered_articles = []
            
            for article in articles:
                if article.get('published_date'):
                    article_date = article['published_date'].date()
                    if start_dt <= article_date <= end_dt:
                        filtered_articles.append(article)
            
            return filtered_articles
            
        except ValueError as e:
            print(f"Error parsing date: {e}")
            print("Please use date format: YYYY-MM-DD (e.g., 2025-08-18)")
            return []
    
    def print_articles(self, articles: List[Dict], show_content: bool = False):
        """Print articles in a formatted way."""
        if not articles:
            print("No articles found in the specified date range.")
            return
        
        print(f"\n{'='*80}")
        print(f"FOUND {len(articles)} ARTICLES IN DATE RANGE")
        print(f"{'='*80}\n")
        
        for article in articles:
            print(f"Article {article['number']}")
            print(f"Title: {article['title']}")
            print(f"URL: {article['url']}")
            print(f"Published: {article['published_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Occurrences: {article['occurrences']}")
            
            if show_content:
                content = article['content']
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"Content: {content}")
            
            print("-" * 80)
            print()
    
    def save_filtered_articles(self, articles: List[Dict], output_file: str, metadata: Dict):
        """Save filtered articles to a new file with metadata."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                # Write metadata header
                file.write("FILTERED ARTICLES - METADATA REPORT\n")
                file.write("=" * 60 + "\n\n")
                
                # Basic query information
                file.write("QUERY INFORMATION:\n")
                file.write("-" * 20 + "\n")
                file.write(f"Date Range Requested: {metadata.get('query_date_range', 'N/A')}\n")
                file.write(f"Actual Date Range: {metadata.get('actual_date_range', 'N/A')}\n")
                file.write(f"Total Articles Found: {metadata.get('total_articles', 0)}\n")
                file.write(f"Generated At: {metadata.get('generated_at', 'N/A')}\n")
                file.write(f"Source File: {metadata.get('source_file', 'N/A')}\n\n")
                
                # Source analysis
                file.write("SOURCE ANALYSIS:\n")
                file.write("-" * 15 + "\n")
                file.write(f"Unique Sources: {metadata.get('unique_sources', 0)}\n")
                file.write("Top Sources:\n")
                for domain, count in metadata.get('top_sources', []):
                    file.write(f"  • {domain}: {count} articles\n")
                file.write("\n")
                
                # Content analysis
                file.write("CONTENT ANALYSIS:\n")
                file.write("-" * 16 + "\n")
                file.write(f"Average Content Length: {metadata.get('avg_content_length', 0)} characters\n")
                file.write(f"Peak Publishing Hour: {metadata.get('peak_publishing_hour', 'N/A')}\n")
                file.write("\n")
                
                # Occurrence distribution
                file.write("OCCURRENCE DISTRIBUTION:\n")
                file.write("-" * 23 + "\n")
                for occurrences, count in sorted(metadata.get('occurrence_distribution', {}).items()):
                    file.write(f"  {occurrences} occurrence(s): {count} articles\n")
                file.write("\n")
                
                file.write("=" * 60 + "\n")
                file.write("ARTICLE DETAILS\n")
                file.write("=" * 60 + "\n\n")
                
                # Write articles
                for article in articles:
                    file.write(f"Article {article['number']}\n")
                    file.write("-" * 30 + "\n")
                    file.write(f"Title: {article['title']}\n")
                    file.write(f"URL: {article['url']}\n")
                    file.write(f"Source: {self.extract_domain(article['url'])}\n")
                    file.write(f"Published: {article['published_date'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write(f"Occurrences: {article['occurrences']}\n")
                    file.write(f"Content Length: {len(article.get('content', ''))} characters\n")
                    file.write(f"Content: {article['content']}\n")
                    file.write("\n" + "=" * 60 + "\n\n")
            
            print(f"Filtered articles with metadata saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving filtered articles: {e}")

def main():
    """Main function to handle command line arguments and execute the query."""
    parser = argparse.ArgumentParser(
        description="Query articles from articles_summary.txt by date range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query_articles.py 2025-08-18 2025-08-24
  python query_articles.py 2025-08-18 2025-08-24 --show-content
  python query_articles.py 2025-08-18 2025-08-24 --output filtered_articles.txt
  python query_articles.py 2025-08-18 2025-08-24 --show-content --output filtered_articles.txt
        """
    )
    
    parser.add_argument('start_date', help='Start date in YYYY-MM-DD format (e.g., 2025-08-18)')
    parser.add_argument('end_date', help='End date in YYYY-MM-DD format (e.g., 2025-08-24)')
    parser.add_argument('--input', '-i', default='articles_summary.txt', 
                       help='Input articles file (default: articles_summary.txt)')
    parser.add_argument('--output', '-o', 
                       help='Output file to save filtered articles')
    parser.add_argument('--show-content', '-c', action='store_true',
                       help='Show article content in output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress verbose output')
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        start_dt = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(args.end_date, '%Y-%m-%d')
        
        if start_dt > end_dt:
            print("Error: Start date must be before or equal to end date.")
            sys.exit(1)
            
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD format (e.g., 2025-08-18)")
        sys.exit(1)
    
    # Initialize query object
    query = ArticleQuery(args.input)
    
    if not args.quiet:
        print(f"Loading articles from: {args.input}")
        print(f"Querying articles from {args.start_date} to {args.end_date}")
    
    # Parse articles
    articles = query.parse_articles_file()
    
    if not articles:
        print("No articles found to query.")
        sys.exit(1)
    
    # Filter by date range
    filtered_articles = query.filter_by_date_range(articles, args.start_date, args.end_date)
    
    # Generate metadata
    metadata = query.generate_metadata(filtered_articles, args.start_date, args.end_date)
    
    # Print results
    if not args.quiet:
        query.print_articles(filtered_articles, args.show_content)
    else:
        print(f"Found {len(filtered_articles)} articles in date range {args.start_date} to {args.end_date}")
    
    # Save to file if requested
    if args.output:
        query.save_filtered_articles(filtered_articles, args.output, metadata)
    
    # Exit with appropriate code
    if filtered_articles:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
