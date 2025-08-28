# Biotech News Pipeline

A comprehensive automation system that transforms RSS feeds into professional content ready for distribution. This pipeline orchestrates the entire workflow from data collection to social media posting, with organized output storage and detailed logging.

## 🚀 Complete Workflow

### **4-Step Pipeline Process:**

1. **📡 RSS Feed Parsing** → Extract articles from biotech RSS feeds
2. **📅 Date Range Filtering** → Focus on specific time periods  
3. **🎙️ Podcast Generation** → Create professional podcast scripts
4. **💼 LinkedIn Post Creation** → Generate social media content

### **Organized Output Structure:**
```
output/
└── run_20250127_143022/
    ├── raw/                    # Original RSS parsed articles
    │   └── articles_summary.txt
    ├── processed/              # Date-filtered articles
    │   └── filtered_articles.txt
    ├── final/                  # Ready-to-use content
    │   ├── podcast_script.txt
    │   ├── linkedin_post.txt
    │   └── linkedin_post_compact.txt
    ├── pipeline_log.txt        # Detailed execution log
    └── pipeline_summary.txt    # Run summary report
```

## 📋 Scripts Overview

### **Core Pipeline Scripts:**

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `pipeline.py` | **Main orchestrator** | RSS feeds, date range | Complete pipeline output |
| `rss_parser.py` | Parse RSS feeds | `sources.txt` | Articles with metadata |
| `query_articles.py` | Filter by date range | Articles summary | Filtered articles |
| `podcast_generator.py` | Generate podcast script | Filtered articles | Professional podcast |
| `linkedin_extractor.py` | Create LinkedIn posts | Podcast script | Social media content |

### **Supporting Files:**
- `sources.txt` - RSS feed URLs
- `PIPELINE_README.md` - Detailed pipeline documentation
- `PODCAST_README.md` - Podcast generator documentation
- `LINKEDIN_README.md` - LinkedIn extractor documentation

## 🎯 Quick Start

### **Prerequisites:**
```bash
# Install Python dependencies
pip install feedparser requests beautifulsoup4

# Ensure sources.txt contains your RSS feed URLs
```

### **Run Complete Pipeline:**
```bash
# Default: Last 7 days
python pipeline.py

# Custom date range
python pipeline.py --start-date 2025-08-18 --end-date 2025-08-24

# Custom output directory
python pipeline.py --output my_reports --days 14

# Single day analysis
python pipeline.py --output daily_reports --days 1
```

### **Individual Scripts:**
```bash
# RSS parsing only
python rss_parser.py

# Date filtering only
python query_articles.py 2025-08-18 2025-08-24

# Podcast generation only
python podcast_generator.py --input filtered.txt

# LinkedIn post only
python linkedin_extractor.py --podcast podcast.txt --articles filtered.txt
```

## 📊 Pipeline Features

### **RSS Feed Parsing (`rss_parser.py`)**
- **Multi-source aggregation**: Combines articles from multiple RSS feeds
- **Duplicate detection**: Identifies and handles duplicate articles
- **Metadata extraction**: Captures title, URL, publication date, content preview
- **Occurrence tracking**: Counts article appearances across sources
- **Error handling**: Graceful handling of network issues and malformed feeds

### **Date Range Filtering (`query_articles.py`)**
- **Flexible date ranges**: Custom start/end dates or relative periods
- **Source analysis**: Provides statistics on article sources
- **Content statistics**: Analyzes article length and distribution
- **Enhanced metadata**: Adds content length and source diversity metrics
- **Filtered output**: Clean, organized article list with metadata

### **Podcast Generation (`podcast_generator.py`)**
- **Impact scoring**: Ranks articles by relevance and importance
- **Topic diversity**: Ensures coverage across biotech categories
- **Narrative flow**: Structures content with opening, main stories, quick hits
- **Professional formatting**: Creates broadcast-ready scripts
- **Source attribution**: Lists all sources at the end
- **Duration control**: Configurable target podcast length

### **LinkedIn Post Creation (`linkedin_extractor.py`)**
- **Clickable titles**: Article titles as markdown links
- **Multiple formats**: Standard and compact versions
- **HTML cleaning**: Removes HTML tags from titles
- **Professional hashtags**: Industry-relevant tags included
- **Title-URL mapping**: Automatic linking of titles to source URLs

## 🎙️ Podcast Features

### **Content Selection Algorithm:**
- **Impact scoring** based on keywords (clinical trial, FDA, breakthrough, etc.)
- **Topic classification** into 10 biotech categories:
  - Therapeutics, Diagnostics, Research, Industry, Technology
  - Genetics, Microbiome, Cancer, Rare Disease, Infectious Disease
- **Hybrid selection** balancing main stories and quick hits
- **Time-based structuring** for optimal flow

### **Output Format:**
```
🎙️ BIOTECH NEWS PODCAST
[Date Range]

=== OPENING ===
Welcome to this week's biotech news roundup...

=== MAIN STORIES ===
Story 1: [Title]
[Detailed summary with context and implications]

Story 2: [Title]
[Detailed summary with context and implications]

=== QUICK HITS ===
• [Brief summary]
• [Brief summary]

=== TRENDS & INSIGHTS ===
[Analysis of common themes and patterns]

=== CLOSING ===
[Wrap-up and forward-looking statements]

=== SOURCES SUMMARY ===
[Complete list of sources used]
```

## 💼 LinkedIn Features

### **Post Formats:**

#### **Standard Format:**
```
🔬 This Week's Top Biotech News

Here are the key developments in biotechnology this week:

1. [Article Title](URL)

2. [Article Title](URL)

#Biotech #Biotechnology #Science #Innovation #Healthcare #Research
```

#### **Compact Format:**
```
🔬 This Week's Top Biotech News

Key developments in biotechnology:

1. [Article Title](URL)
2. [Article Title](URL)

#Biotech #Biotechnology #Science #Innovation #Healthcare #Research
```

## 🔧 Configuration

### **RSS Sources (`sources.txt`):**
```
https://phys.org/rss-feed/biology-news/
https://www.sciencedaily.com/rss/health_medicine/biotechnology.xml
https://www.labiotech.eu/feed/
https://www.genengnews.com/feed/
https://endpoints.news/feed/
https://www.biopharmadive.com/rss/
https://www.fiercebiotech.com/rss/xml
https://bio.news/feed/
https://www.biotech.ca/news/feed/
https://www.technologyreview.com/topic/biotechnology/feed/
https://biotechexpressmag.com/feed/
https://o2h.com/feed/
https://bioengineer.org/feed/
```

### **Command Line Options:**
```bash
# Pipeline options
--output, -o          Output directory (default: output)
--start-date, -s      Start date for filtering (YYYY-MM-DD)
--end-date, -e        End date for filtering (YYYY-MM-DD)
--days, -d            Number of days to look back (default: 7)

# Podcast options
--input, -i           Input articles file
--output, -o          Output podcast file
--duration, -d        Target duration in minutes (default: 10)

# LinkedIn options
--podcast, -p         Podcast script file
--articles, -a        Articles file with URLs
--output, -o          Output LinkedIn post file
--compact, -c         Generate compact format
```

## 📈 Usage Examples

### **Daily Reports:**
```bash
# Generate daily report
python pipeline.py --output daily_reports --days 1

# Schedule with cron (daily at 9 AM)
0 9 * * * cd /path/to/news-podcast && python pipeline.py --output daily_reports --days 1
```

### **Weekly Summaries:**
```bash
# Generate weekly summary
python pipeline.py --output weekly_reports --days 7

# Schedule with cron (every Monday at 8 AM)
0 8 * * 1 cd /path/to/news-podcast && python pipeline.py --output weekly_reports --days 7
```

### **Custom Analysis:**
```bash
# Monthly analysis
python pipeline.py --output monthly_reports --start-date 2025-08-01 --end-date 2025-08-31

# Event-specific coverage
python pipeline.py --output conference_coverage --start-date 2025-08-15 --end-date 2025-08-20

# Recent developments (last 3 days)
python pipeline.py --output recent_news --days 3
```

### **Individual Component Usage:**
```bash
# Parse RSS feeds only
python rss_parser.py

# Filter articles for specific date range
python query_articles.py 2025-08-18 2025-08-24 --output filtered_articles.txt

# Generate podcast from filtered articles
python podcast_generator.py --input filtered_articles.txt --output podcast_script.txt

# Create LinkedIn post from podcast
python linkedin_extractor.py --podcast podcast_script.txt --articles filtered_articles.txt --output linkedin_post.txt
```

## 🛠️ Technical Details

### **Dependencies:**
- Python 3.7+
- `feedparser` - RSS feed parsing
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `datetime` - Date handling
- `pathlib` - File path management

### **Installation:**
```bash
# Clone repository
git clone <repository-url>
cd news-podcast

# Install dependencies
pip install feedparser requests beautifulsoup4

# Set up RSS sources
# Edit sources.txt with your preferred RSS feeds
```

### **File Structure:**
```
news-podcast/
├── pipeline.py              # Main pipeline orchestrator
├── rss_parser.py            # RSS feed parser
├── query_articles.py        # Date range filter
├── podcast_generator.py     # Podcast script generator
├── linkedin_extractor.py    # LinkedIn post creator
├── sources.txt              # RSS feed URLs
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── PIPELINE_README.md      # Detailed pipeline docs
├── PODCAST_README.md       # Podcast generator docs
├── LINKEDIN_README.md      # LinkedIn extractor docs
├── CLEANUP_SUMMARY.md      # Cleanup documentation
└── example_output/         # Example pipeline run
    └── run_20250827_121133/
        ├── raw/
        ├── processed/
        ├── final/
        ├── pipeline_log.txt
        └── pipeline_summary.txt
```

## 🎯 Benefits

✅ **Complete Automation**: End-to-end workflow from RSS to social media
✅ **Professional Quality**: Production-ready content generation
✅ **Organized Output**: Structured file organization with clear naming
✅ **Comprehensive Logging**: Detailed execution tracking and error reporting
✅ **Flexible Configuration**: Customizable date ranges and output locations
✅ **Easy Integration**: Works with existing scripts and workflows
✅ **Scalable**: Handles multiple runs with unique identifiers
✅ **Reproducible**: Consistent results with detailed logging

## 🔄 Automation & Scheduling

### **Cron Job Examples:**
```bash
# Daily reports at 9 AM
0 9 * * * cd /path/to/news-podcast && python pipeline.py --output daily_reports --days 1

# Weekly summaries every Monday at 8 AM
0 8 * * 1 cd /path/to/news-podcast && python pipeline.py --output weekly_reports --days 7

# Monthly analysis on the 1st at 7 AM
0 7 1 * * cd /path/to/news-podcast && python pipeline.py --output monthly_reports --start-date $(date -d '1 month ago' +%Y-%m-01) --end-date $(date +%Y-%m-%d)
```

### **Batch Processing:**
```bash
# Process multiple date ranges
for days in 1 3 7 14 30; do
    python pipeline.py --output batch_reports --days $days
done
```

## 📝 Best Practices

### **For Regular Use:**
1. **Schedule runs**: Use cron jobs for automated daily/weekly reports
2. **Monitor logs**: Check pipeline_log.txt for any issues
3. **Archive results**: Keep historical runs for comparison
4. **Customize output**: Use meaningful output directory names

### **For Content Strategy:**
1. **Consistent timing**: Run at regular intervals for audience expectations
2. **Quality review**: Always review generated content before posting
3. **Engagement tracking**: Monitor LinkedIn post performance
4. **Iterative improvement**: Use feedback to refine the pipeline

### **For Technical Maintenance:**
1. **Update sources**: Regularly review and update RSS feed sources
2. **Monitor dependencies**: Keep Python packages updated
3. **Backup data**: Archive important pipeline runs
4. **Performance monitoring**: Track execution times and resource usage

## 🚀 Getting Started

### **Step-by-Step Setup:**

1. **Install Dependencies:**
   ```bash
   pip install feedparser requests beautifulsoup4
   ```

2. **Configure RSS Sources:**
   - Edit `sources.txt` with your preferred RSS feed URLs
   - Ensure URLs are accessible and valid

3. **Test the Pipeline:**
   ```bash
   python pipeline.py --output test_run --days 1
   ```

4. **Review Output:**
   - Check `test_run/` directory for generated content
   - Review `pipeline_log.txt` for execution details
   - Examine `pipeline_summary.txt` for run overview

5. **Customize Settings:**
   - Adjust date ranges as needed
   - Modify output directory names
   - Configure podcast duration preferences

6. **Set Up Automation:**
   - Create cron jobs for regular execution
   - Monitor logs for any issues
   - Archive important runs

### **Example First Run:**
```bash
# Run pipeline for last 3 days
python pipeline.py --output first_run --days 3

# Check results
ls first_run/
cat first_run/*/pipeline_summary.txt
cat first_run/*/final/linkedin_post.txt
```

## 📊 Example Output

The `example_output/` directory contains a complete pipeline run demonstrating:
- **98 articles** processed from 1 day
- **Professional podcast script** (13.3 minutes)
- **LinkedIn posts** with clickable titles (standard & compact)
- **Complete logging** and execution summary

This serves as a reference for expected output format and quality.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and features.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

The Biotech News Pipeline transforms raw RSS feeds into professional, engagement-ready content with complete automation and organization! 🎉
