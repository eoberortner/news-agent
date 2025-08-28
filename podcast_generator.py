#!/usr/bin/env python3
"""
Podcast Generator Script

This script implements a hybrid approach to generate a 10-minute podcast summary
from filtered articles. It uses occurrence-based selection, impact scoring,
topic diversity, and narrative flow construction.
"""

import argparse
import re
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import sys
import os
from collections import defaultdict, Counter
import random

class PodcastGenerator:
    def __init__(self, articles_file: str = "filtered_articles.txt"):
        self.articles_file = articles_file
        self.articles = []
        self.selected_articles = []
        
        # Impact keywords and their weights
        self.impact_keywords = {
            'clinical trial': 5,
            'fda': 5,
            'approval': 5,
            'breakthrough': 4,
            'discovery': 4,
            'first': 4,
            'novel': 4,
            'treatment': 3,
            'cure': 3,
            'drug': 3,
            'therapy': 3,
            'funding': 2,
            'investment': 2,
            'partnership': 2,
            'collaboration': 2,
            'study': 2,
            'research': 2,
            'development': 2
        }
        
        # Topic categories for diversity
        self.topic_categories = {
            'therapeutics': ['treatment', 'therapy', 'drug', 'cure', 'clinical trial', 'fda', 'approval'],
            'diagnostics': ['diagnostic', 'detection', 'screening', 'test', 'biomarker'],
            'research': ['research', 'study', 'discovery', 'breakthrough', 'novel'],
            'industry': ['funding', 'investment', 'partnership', 'collaboration', 'company'],
            'technology': ['technology', 'platform', 'tool', 'device', 'ai', 'machine learning'],
            'genetics': ['gene', 'genetic', 'dna', 'rna', 'genome', 'crispr'],
            'microbiome': ['microbiome', 'bacteria', 'microbial', 'gut', 'microbiome'],
            'cancer': ['cancer', 'oncology', 'tumor', 'carcinoma', 'leukemia'],
            'rare_disease': ['rare disease', 'orphan', 'genetic disorder'],
            'infectious_disease': ['infection', 'virus', 'bacterial', 'pathogen', 'vaccine']
        }
        
    def parse_articles_file(self) -> List[Dict]:
        """Parse the filtered articles file and extract article information."""
        if not os.path.exists(self.articles_file):
            print(f"Error: Articles file '{self.articles_file}' not found.")
            return []
        
        articles = []
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
                elif line.startswith("Source: "):
                    current_article['source'] = line[8:]
                elif line.startswith("Published: "):
                    date_str = line[11:]
                    try:
                        current_article['published_date'] = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        current_article['published_date'] = None
                elif line.startswith("Occurrences: "):
                    current_article['occurrences'] = int(line[13:])
                elif line.startswith("Content Length: "):
                    content_length_str = line[16:]
                    # Remove "characters" suffix if present
                    content_length_str = content_length_str.replace(" characters", "")
                    try:
                        current_article['content_length'] = int(content_length_str)
                    except ValueError:
                        current_article['content_length'] = 0
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
    
    def calculate_impact_score(self, article: Dict) -> float:
        """Calculate impact score based on keywords and other factors."""
        score = 0.0
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        
        # Keyword scoring
        for keyword, weight in self.impact_keywords.items():
            if keyword in text:
                score += weight
        
        # Occurrence bonus
        score += article.get('occurrences', 1) * 2
        
        # Content length bonus (longer articles may have more substance)
        content_length = article.get('content_length', 0)
        if content_length > 300:
            score += 1
        
        # Recency bonus (more recent articles get slight priority)
        if article.get('published_date'):
            days_old = (datetime.now() - article['published_date']).days
            if days_old <= 1:
                score += 2
            elif days_old <= 3:
                score += 1
        
        return score
    
    def classify_topic(self, article: Dict) -> str:
        """Classify article into topic categories."""
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        
        topic_scores = defaultdict(int)
        
        for topic, keywords in self.topic_categories.items():
            for keyword in keywords:
                if keyword in text:
                    topic_scores[topic] += 1
        
        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def select_articles_hybrid(self, articles: List[Dict], target_duration: int = 600) -> List[Dict]:
        """Select articles using hybrid approach for target duration (in seconds)."""
        if not articles:
            return []
        
        # Calculate impact scores and classify topics
        for article in articles:
            article['impact_score'] = self.calculate_impact_score(article)
            article['topic'] = self.classify_topic(article)
        
        # Sort by impact score
        articles.sort(key=lambda x: x['impact_score'], reverse=True)
        
        selected_articles = []
        topic_coverage = defaultdict(int)
        estimated_duration = 0
        
        # Target time allocation
        main_stories_time = target_duration * 0.6  # 60% for main stories
        quick_hits_time = target_duration * 0.3    # 30% for quick hits
        analysis_time = target_duration * 0.1      # 10% for analysis
        
        # Select main stories (5-7 articles, 2-3 minutes each)
        main_stories = []
        for article in articles[:10]:  # Consider top 10
            if len(main_stories) >= 6:  # Max 6 main stories
                break
            
            # Ensure topic diversity
            if topic_coverage[article['topic']] < 2:  # Max 2 per topic
                main_stories.append(article)
                topic_coverage[article['topic']] += 1
                estimated_duration += 180  # 3 minutes per main story
        
        # Select quick hits (10-15 articles, 15-30 seconds each)
        quick_hits = []
        remaining_articles = [a for a in articles if a not in main_stories]
        
        for article in remaining_articles[:15]:  # Consider next 15
            if len(quick_hits) >= 12:  # Max 12 quick hits
                break
            
            # Ensure topic diversity
            if topic_coverage[article['topic']] < 3:  # Max 3 per topic
                quick_hits.append(article)
                topic_coverage[article['topic']] += 1
                estimated_duration += 20  # 20 seconds per quick hit
        
        selected_articles = main_stories + quick_hits
        
        print(f"Selected {len(main_stories)} main stories and {len(quick_hits)} quick hits")
        print(f"Estimated duration: {estimated_duration/60:.1f} minutes")
        
        return selected_articles
    
    def generate_podcast_script(self, articles: List[Dict]) -> str:
        """Generate a podcast script from selected articles."""
        if not articles:
            return "No articles selected for podcast generation."
        
        # Separate main stories and quick hits
        main_stories = articles[:6]  # First 6 are main stories
        quick_hits = articles[6:]    # Rest are quick hits
        
        script = []
        
        # Opening
        script.append("=== BIOTECH WEEKLY PODCAST ===")
        script.append("")
        script.append("Welcome to this week's biotech news roundup. I'm your host, and today we're covering the latest developments in biotechnology, from breakthrough discoveries to industry updates.")
        script.append("")
        
        # Main stories section
        script.append("=== MAIN STORIES ===")
        script.append("")
        
        for i, article in enumerate(main_stories, 1):
            script.append(f"Story {i}: {article['title']}")
            script.append("")
            
            # Generate summary
            summary = self.generate_article_summary(article, detailed=True)
            script.append(summary)
            script.append("")
            script.append("---")
            script.append("")
        
        # Quick hits section
        if quick_hits:
            script.append("=== QUICK HITS ===")
            script.append("")
            script.append("Now for some quick updates from around the biotech world:")
            script.append("")
            
            for i, article in enumerate(quick_hits, 1):
                script.append(f"• {article['title']}")
                summary = self.generate_article_summary(article, detailed=False)
                script.append(f"  {summary}")
                script.append("")
        
        # Closing and trends
        script.append("=== TRENDS & INSIGHTS ===")
        script.append("")
        trends = self.analyze_trends(articles)
        script.append(trends)
        script.append("")
        script.append("That wraps up this week's biotech news. Thanks for listening, and we'll see you next week with more updates from the world of biotechnology.")
        script.append("")
        
        # Add source summary
        source_summary = self.generate_source_summary(articles)
        script.append(source_summary)
        
        return "\n".join(script)
    
    def generate_article_summary(self, article: Dict, detailed: bool = False) -> str:
        """Generate a summary for an article."""
        title = article.get('title', '')
        content = article.get('content', '')
        
        if detailed:
            # Detailed summary for main stories
            # Extract key information from content
            sentences = content.split('. ')
            if len(sentences) > 1:
                summary = sentences[0] + '.'
                if len(sentences) > 2:
                    summary += ' ' + sentences[1] + '.'
            else:
                summary = content[:200] + '...' if len(content) > 200 else content
            
            return summary
        else:
            # Brief summary for quick hits - ensure complete full sentences
            sentences = content.split('. ')
            
            if len(sentences) >= 1:
                # Take the first complete sentence
                first_sentence = sentences[0].strip()
                if first_sentence:
                    # Ensure it ends with proper punctuation
                    if not first_sentence.endswith(('.', '!', '?')):
                        first_sentence += '.'
                    
                    # If the sentence is too long, try to find a shorter complete sentence
                    if len(first_sentence) > 200:
                        # Look for the second sentence if available
                        if len(sentences) >= 2:
                            second_sentence = sentences[1].strip()
                            if second_sentence and len(second_sentence) <= 200:
                                if not second_sentence.endswith(('.', '!', '?')):
                                    second_sentence += '.'
                                return second_sentence
                        
                        # If no good second sentence, try to find a natural break in the first sentence
                        # Look for common break points like "and", "but", "however", etc.
                        break_points = [' and ', ' but ', ' however, ', ' although ', ' while ', ' though ']
                        for break_point in break_points:
                            if break_point in first_sentence:
                                parts = first_sentence.split(break_point, 1)
                                if len(parts[0]) <= 200:
                                    return parts[0] + '.'
                    
                    # If the sentence is reasonable length, return it as is
                    if len(first_sentence) <= 200:
                        return first_sentence
            
            # Fallback: create a simple summary without truncation
            # Take the first 150 characters and try to end at a word boundary
            if len(content) > 150:
                words = content[:150].split()
                if len(words) > 3:  # Ensure we have enough words
                    # Remove the last word if it might be cut off
                    summary = ' '.join(words[:-1])
                    # Ensure it ends with proper punctuation
                    if not summary.endswith(('.', '!', '?')):
                        summary += '.'
                    return summary
            
            # If content is short enough, return as is
            summary = content.strip()
            if not summary.endswith(('.', '!', '?')):
                summary += '.'
            return summary
    
    def generate_source_summary(self, articles: List[Dict]) -> str:
        """Generate a summary of all sources used in the podcast."""
        sources = [article.get('source', '') for article in articles]
        source_counts = Counter(sources)
        
        summary = []
        summary.append("=== SOURCES SUMMARY ===")
        summary.append("")
        summary.append("This podcast was compiled from the following sources:")
        summary.append("")
        
        # Sort sources by article count
        sorted_sources = source_counts.most_common()
        
        for source, count in sorted_sources:
            summary.append(f"• {source}: {count} article{'s' if count > 1 else ''}")
        
        summary.append("")
        summary.append(f"Total sources: {len(source_counts)}")
        summary.append(f"Total articles: {len(articles)}")
        
        return "\n".join(summary)
    
    def analyze_trends(self, articles: List[Dict]) -> str:
        """Analyze trends in the selected articles."""
        topics = [article.get('topic', 'general') for article in articles]
        topic_counts = Counter(topics)
        
        # Find most common topics
        top_topics = topic_counts.most_common(3)
        
        # Analyze sources
        sources = [article.get('source', '') for article in articles]
        source_counts = Counter(sources)
        
        trends = "Looking at this week's developments, "
        
        if top_topics:
            main_topic = top_topics[0][0]
            trends += f"the focus has been on {main_topic.replace('_', ' ')} research, "
            
            if len(top_topics) > 1:
                second_topic = top_topics[1][0]
                trends += f"followed by {second_topic.replace('_', ' ')}. "
            else:
                trends += "showing a concentrated effort in this area. "
        
        # Add source diversity comment
        unique_sources = len(source_counts)
        trends += f"We're seeing coverage from {unique_sources} different sources, "
        trends += "indicating broad industry interest in these developments."
        
        return trends
    
    def save_podcast_script(self, script: str, output_file: str):
        """Save the podcast script to a file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(script)
            
            print(f"Podcast script saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving podcast script: {e}")
    
    def generate_podcast(self, target_duration: int = 600) -> str:
        """Generate a complete podcast from articles."""
        # Parse articles
        articles = self.parse_articles_file()
        
        if not articles:
            return "No articles found to generate podcast."
        
        # Select articles using hybrid approach
        selected_articles = self.select_articles_hybrid(articles, target_duration)
        
        if not selected_articles:
            return "No articles selected for podcast generation."
        
        # Generate script
        script = self.generate_podcast_script(selected_articles)
        
        return script

def main():
    """Main function to handle command line arguments and execute podcast generation."""
    parser = argparse.ArgumentParser(
        description="Generate a podcast script from filtered articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python podcast_generator.py
  python podcast_generator.py --duration 480 --output podcast_script.txt
  python podcast_generator.py --input my_articles.txt --duration 720
        """
    )
    
    parser.add_argument('--input', '-i', default='filtered_articles.txt', 
                       help='Input articles file (default: filtered_articles.txt)')
    parser.add_argument('--output', '-o', default='podcast_script.txt',
                       help='Output script file (default: podcast_script.txt)')
    parser.add_argument('--duration', '-d', type=int, default=600,
                       help='Target duration in seconds (default: 600 = 10 minutes)')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = PodcastGenerator(args.input)
    
    print(f"Generating {args.duration/60:.1f}-minute podcast from {args.input}")
    
    # Generate podcast
    script = generator.generate_podcast(args.duration)
    
    # Save script
    generator.save_podcast_script(script, args.output)
    
    print("Podcast generation complete!")

if __name__ == "__main__":
    main()
