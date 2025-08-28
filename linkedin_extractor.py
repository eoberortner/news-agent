#!/usr/bin/env python3
"""
LinkedIn Post Extractor

This script extracts article titles and URLs from a generated podcast script
to create a LinkedIn post with clickable links.
"""

import argparse
import re
import os
from typing import List, Dict, Tuple

class LinkedInExtractor:
    def __init__(self, podcast_file: str = "complete_sentences.txt", articles_file: str = "enhanced_filtered_articles.txt"):
        self.podcast_file = podcast_file
        self.articles_file = articles_file
        self.article_data = {}
        self.podcast_articles = []
        
    def parse_articles_file(self) -> Dict[str, str]:
        """Parse the articles file to get title-URL mappings."""
        if not os.path.exists(self.articles_file):
            print(f"Error: Articles file '{self.articles_file}' not found.")
            return {}
        
        title_url_map = {}
        current_article = {}
        in_metadata = True
        
        try:
            with open(self.articles_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip metadata section
                if line.startswith("ARTICLE DETAILS"):
                    in_metadata = False
                    i += 1
                    continue
                
                if in_metadata:
                    i += 1
                    continue
                
                # Look for article start pattern
                if line.startswith("Article ") and "------------------------------" in lines[i+1]:
                    # Save previous article if exists
                    if current_article and 'title' in current_article and 'url' in current_article:
                        title_url_map[current_article['title']] = current_article['url']
                    
                    # Start new article
                    current_article = {}
                    i += 2  # Skip the separator line
                    continue
                
                # Parse article fields
                if line.startswith("Title: "):
                    current_article['title'] = line[7:]
                elif line.startswith("URL: "):
                    current_article['url'] = line[5:]
                
                i += 1
            
            # Add the last article
            if current_article and 'title' in current_article and 'url' in current_article:
                title_url_map[current_article['title']] = current_article['url']
            
            print(f"Successfully parsed {len(title_url_map)} articles from {self.articles_file}")
            return title_url_map
            
        except Exception as e:
            print(f"Error parsing articles file: {e}")
            return {}
    
    def extract_podcast_articles(self) -> List[str]:
        """Extract article titles from the podcast script."""
        if not os.path.exists(self.podcast_file):
            print(f"Error: Podcast file '{self.podcast_file}' not found.")
            return []
        
        podcast_articles = []
        in_quick_hits = False
        
        try:
            with open(self.podcast_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Track when we're in the quick hits section
                if line == "=== QUICK HITS ===":
                    in_quick_hits = True
                    continue
                
                # Stop when we reach the end of quick hits
                if in_quick_hits and line.startswith("==="):
                    break
                
                # Extract main story titles (before quick hits)
                if not in_quick_hits and line.startswith("Story ") and ":" in line:
                    title = line.split(":", 1)[1].strip()
                    # Clean HTML tags from title
                    title = re.sub(r'<[^>]+>', '', title)
                    podcast_articles.append(title)
                
                # Extract quick hit titles
                elif in_quick_hits and line.startswith("• ") and not line.startswith("• " + "="):
                    title = line[2:].strip()
                    # Clean HTML tags from title
                    title = re.sub(r'<[^>]+>', '', title)
                    podcast_articles.append(title)
            
            print(f"Successfully extracted {len(podcast_articles)} articles from podcast")
            return podcast_articles
            
        except Exception as e:
            print(f"Error extracting podcast articles: {e}")
            return []
    
    def generate_linkedin_post(self) -> str:
        """Generate a LinkedIn post with article titles and URLs."""
        # Parse articles file to get title-URL mappings
        title_url_map = self.parse_articles_file()
        
        # Extract articles from podcast
        podcast_articles = self.extract_podcast_articles()
        
        if not podcast_articles:
            return "No articles found in podcast."
        
        if not title_url_map:
            return "No article data available for URL mapping."
        
        # Generate LinkedIn post
        post_lines = []
        post_lines.append("🔬 This Week's Top Biotech News")
        post_lines.append("")
        post_lines.append("Here are the key developments in biotechnology this week:")
        post_lines.append("")
        
        # Add articles with URLs as clickable titles
        for i, title in enumerate(podcast_articles, 1):
            if title in title_url_map:
                url = title_url_map[title]
                post_lines.append(f"{i}. [{title}]({url})")
                post_lines.append("")
            else:
                # If URL not found, just add the title
                post_lines.append(f"{i}. {title}")
                post_lines.append("")
        
        post_lines.append("#Biotech #Biotechnology #Science #Innovation #Healthcare #Research")
        
        return "\n".join(post_lines)
    
    def generate_linkedin_post_compact(self) -> str:
        """Generate a more compact LinkedIn post format."""
        # Parse articles file to get title-URL mappings
        title_url_map = self.parse_articles_file()
        
        # Extract articles from podcast
        podcast_articles = self.extract_podcast_articles()
        
        if not podcast_articles:
            return "No articles found in podcast."
        
        if not title_url_map:
            return "No article data available for URL mapping."
        
        # Generate compact LinkedIn post
        post_lines = []
        post_lines.append("🔬 This Week's Top Biotech News")
        post_lines.append("")
        post_lines.append("Key developments in biotechnology:")
        post_lines.append("")
        
        # Add articles with URLs as clickable titles in compact format
        for i, title in enumerate(podcast_articles, 1):
            if title in title_url_map:
                url = title_url_map[title]
                post_lines.append(f"{i}. [{title}]({url})")
            else:
                post_lines.append(f"{i}. {title}")
        
        post_lines.append("")
        post_lines.append("#Biotech #Biotechnology #Science #Innovation #Healthcare #Research")
        
        return "\n".join(post_lines)
    
    def save_linkedin_post(self, post_content: str, output_file: str):
        """Save the LinkedIn post to a file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(post_content)
            
            print(f"LinkedIn post saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving LinkedIn post: {e}")

def main():
    """Main function to handle command line arguments and execute LinkedIn post generation."""
    parser = argparse.ArgumentParser(
        description="Extract article titles and URLs from podcast for LinkedIn posting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python linkedin_extractor.py
  python linkedin_extractor.py --podcast my_podcast.txt --articles my_articles.txt
  python linkedin_extractor.py --compact --output linkedin_post.txt
        """
    )
    
    parser.add_argument('--podcast', '-p', default='complete_sentences.txt', 
                       help='Podcast script file (default: complete_sentences.txt)')
    parser.add_argument('--articles', '-a', default='enhanced_filtered_articles.txt',
                       help='Articles file with URLs (default: enhanced_filtered_articles.txt)')
    parser.add_argument('--output', '-o', default='linkedin_post.txt',
                       help='Output LinkedIn post file (default: linkedin_post.txt)')
    parser.add_argument('--compact', '-c', action='store_true',
                       help='Generate compact format LinkedIn post')
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = LinkedInExtractor(args.podcast, args.articles)
    
    print(f"Extracting LinkedIn post from {args.podcast}")
    
    # Generate LinkedIn post
    if args.compact:
        post_content = extractor.generate_linkedin_post_compact()
    else:
        post_content = extractor.generate_linkedin_post()
    
    # Save post
    extractor.save_linkedin_post(post_content, args.output)
    
    print("LinkedIn post generation complete!")

if __name__ == "__main__":
    main()
