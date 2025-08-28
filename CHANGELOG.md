# Changelog

All notable changes to the Biotech News Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-27

### Added
- **Complete pipeline system** with 4-step workflow
- **RSS feed parser** (`rss_parser.py`) with multi-source aggregation
- **Date range filter** (`query_articles.py`) with flexible date handling
- **Podcast generator** (`podcast_generator.py`) with impact scoring and topic diversity
- **LinkedIn extractor** (`linkedin_extractor.py`) with clickable titles
- **Main pipeline orchestrator** (`pipeline.py`) with organized output structure
- **Comprehensive documentation** including README, individual script docs, and examples
- **Error handling and logging** throughout all components
- **HTML tag cleaning** for LinkedIn post titles
- **Source attribution** in podcast scripts
- **Multiple output formats** (standard and compact LinkedIn posts)
- **Automated directory structure** with timestamps and organized subdirectories
- **Example output** demonstrating complete pipeline functionality

### Features
- **Impact scoring algorithm** based on biotech keywords
- **Topic classification** into 10 biotech categories
- **Hybrid article selection** balancing main stories and quick hits
- **Professional podcast formatting** with narrative flow
- **Clickable LinkedIn titles** using markdown format
- **Flexible date range configuration** (custom dates, relative periods)
- **Duplicate article detection** across RSS sources
- **Comprehensive metadata extraction** and analysis
- **Configurable podcast duration** targeting
- **Professional hashtag inclusion** for social media

### Technical
- **Python 3.7+ compatibility**
- **Modular architecture** with separate components
- **Command-line interface** with argparse
- **Subprocess management** for pipeline orchestration
- **File path handling** with pathlib
- **Exception handling** and graceful error recovery
- **Logging system** with timestamps and status tracking
- **Output organization** with raw/processed/final structure

### Documentation
- **Main README.md** with comprehensive usage guide
- **PIPELINE_README.md** with detailed pipeline documentation
- **PODCAST_README.md** with podcast generator specifics
- **LINKEDIN_README.md** with LinkedIn extractor details
- **CLEANUP_SUMMARY.md** documenting project cleanup
- **CHANGELOG.md** with development history
- **MIT License** for open source distribution

### Configuration
- **RSS sources configuration** (`sources.txt`)
- **Python dependencies** (`requirements.txt`)
- **Git ignore rules** for generated files
- **Example output** demonstrating expected results

### Output Structure
```
output/
└── run_YYYYMMDD_HHMMSS/
    ├── raw/                    # Original RSS parsed articles
    ├── processed/              # Date-filtered articles
    ├── final/                  # Ready-to-use content
    ├── pipeline_log.txt        # Execution log
    └── pipeline_summary.txt    # Run summary
```

### Supported RSS Sources
- Phys.org Biology News
- Science Daily Biotechnology
- Labiotech.eu
- Genetic Engineering News
- Endpoints News
- BioPharma Dive
- Fierce Biotech
- Bio.news
- Biotech.ca
- MIT Technology Review
- Biotech Express Magazine
- O2h.com
- Bioengineer.org

### Command Line Options
- `--output, -o`: Output directory
- `--start-date, -s`: Start date for filtering
- `--end-date, -e`: End date for filtering
- `--days, -d`: Number of days to look back
- `--input, -i`: Input articles file
- `--duration, -d`: Target podcast duration
- `--podcast, -p`: Podcast script file
- `--articles, -a`: Articles file with URLs
- `--compact, -c`: Generate compact format

### Initial Release Features
- **Complete automation** from RSS feeds to social media content
- **Professional quality** output ready for immediate use
- **Scalable architecture** supporting multiple RSS sources
- **Comprehensive logging** for monitoring and debugging
- **Flexible configuration** for various use cases
- **Production-ready** code with error handling
- **Open source** with MIT license

---

## Development Notes

### Architecture Decisions
- **Modular design**: Each component can be used independently
- **Pipeline orchestration**: Main script coordinates all steps
- **Organized output**: Clear directory structure with timestamps
- **Error isolation**: Pipeline stops at first failure with clear indication
- **Logging integration**: All steps logged with timestamps and status

### Quality Assurance
- **Comprehensive testing** of all pipeline components
- **Error handling** for network issues and malformed feeds
- **Input validation** for date ranges and file paths
- **Output verification** ensuring generated content quality
- **Documentation coverage** for all features and usage

### Performance Considerations
- **Efficient RSS parsing** with duplicate detection
- **Optimized date filtering** with metadata analysis
- **Smart content selection** balancing quality and quantity
- **Streamlined output generation** with minimal processing overhead

### Future Enhancements
- **Additional RSS sources** support
- **Custom topic categories** configuration
- **Advanced content scoring** algorithms
- **Multiple output formats** (Twitter, email, etc.)
- **Web interface** for configuration and monitoring
- **API integration** for external content sources
- **Analytics dashboard** for performance tracking
