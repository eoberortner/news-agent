#!/usr/bin/env python3
"""
Biotech News Pipeline

This script orchestrates the complete biotech news pipeline:
1. RSS Feed Parsing
2. Date Range Filtering
3. Podcast Generation
4. LinkedIn Post Creation

All output files are organized in a specified directory structure.
"""

import argparse
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import shutil

class BiotechPipeline:
    def __init__(self, output_dir: str = "output", date_range: tuple = None):
        self.output_dir = Path(output_dir)
        self.date_range = date_range
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"run_{self.timestamp}"
        
        # Create directory structure
        self.setup_directories()
        
        # File paths for this run
        self.articles_file = self.output_dir / self.run_id / "articles_summary.txt"
        self.filtered_articles_file = self.output_dir / self.run_id / "filtered_articles.txt"
        self.podcast_file = self.output_dir / self.run_id / "podcast_script.txt"
        self.linkedin_post_file = self.output_dir / self.run_id / "linkedin_post.txt"
        self.linkedin_compact_file = self.output_dir / self.run_id / "linkedin_post_compact.txt"
        self.pipeline_log_file = self.output_dir / self.run_id / "pipeline_log.txt"
        
    def setup_directories(self):
        """Create the directory structure for output files."""
        # Main output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Run-specific directory
        run_dir = self.output_dir / self.run_id
        run_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (run_dir / "raw").mkdir(exist_ok=True)
        (run_dir / "processed").mkdir(exist_ok=True)
        (run_dir / "final").mkdir(exist_ok=True)
        
        print(f"Created output directory structure: {run_dir}")
    
    def log_step(self, step: str, message: str, success: bool = True):
        """Log a pipeline step with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ SUCCESS" if success else "❌ FAILED"
        log_entry = f"[{timestamp}] {step}: {message} - {status}"
        
        # Print to console
        print(log_entry)
        
        # Write to log file
        with open(self.pipeline_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def run_command(self, command: list, step_name: str) -> bool:
        """Run a command and log the result."""
        try:
            self.log_step(step_name, f"Running: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                self.log_step(step_name, "Command completed successfully")
                if result.stdout:
                    print(f"Output: {result.stdout.strip()}")
                return True
            else:
                self.log_step(step_name, f"Command failed: {result.stderr}", success=False)
                return False
                
        except Exception as e:
            self.log_step(step_name, f"Exception occurred: {str(e)}", success=False)
            return False
    
    def step_1_parse_rss_feeds(self) -> bool:
        """Step 1: Parse RSS feeds and generate articles summary."""
        command = [
            "python", "rss_parser.py"
        ]
        
        success = self.run_command(command, "RSS Feed Parsing")
        
        if success:
            # The RSS parser creates articles_summary.txt in the current directory
            # Move it to the raw directory
            source_file = Path("articles_summary.txt")
            if source_file.exists():
                raw_file = self.output_dir / self.run_id / "raw" / "articles_summary.txt"
                shutil.move(str(source_file), str(raw_file))
                self.articles_file = raw_file
                return True
            else:
                self.log_step("RSS Feed Parsing", "articles_summary.txt not found after parsing", success=False)
                return False
            
        return success
    
    def step_2_filter_by_date_range(self) -> bool:
        """Step 2: Filter articles by date range."""
        if not self.date_range:
            # Use default date range (last 7 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
        else:
            start_str, end_str = self.date_range
        
        command = [
            "python", "query_articles.py",
            start_str, end_str,
            "--input", str(self.articles_file),
            "--output", str(self.filtered_articles_file)
        ]
        
        success = self.run_command(command, f"Date Range Filtering ({start_str} to {end_str})")
        
        if success:
            # Move to processed directory
            processed_file = self.output_dir / self.run_id / "processed" / "filtered_articles.txt"
            shutil.move(str(self.filtered_articles_file), str(processed_file))
            self.filtered_articles_file = processed_file
            
        return success
    
    def step_3_generate_podcast(self) -> bool:
        """Step 3: Generate podcast script from filtered articles."""
        command = [
            "python", "podcast_generator.py",
            "--input", str(self.filtered_articles_file),
            "--output", str(self.podcast_file)
        ]
        
        success = self.run_command(command, "Podcast Generation")
        
        if success:
            # Move to final directory
            final_file = self.output_dir / self.run_id / "final" / "podcast_script.txt"
            shutil.move(str(self.podcast_file), str(final_file))
            self.podcast_file = final_file
            
        return success
    
    def step_4_create_linkedin_posts(self) -> bool:
        """Step 4: Create LinkedIn posts from podcast script."""
        # Standard LinkedIn post
        command_standard = [
            "python", "linkedin_extractor.py",
            "--podcast", str(self.podcast_file),
            "--articles", str(self.filtered_articles_file),
            "--output", str(self.linkedin_post_file)
        ]
        
        success_standard = self.run_command(command_standard, "LinkedIn Post Generation (Standard)")
        
        # Compact LinkedIn post
        command_compact = [
            "python", "linkedin_extractor.py",
            "--podcast", str(self.podcast_file),
            "--articles", str(self.filtered_articles_file),
            "--compact",
            "--output", str(self.linkedin_compact_file)
        ]
        
        success_compact = self.run_command(command_compact, "LinkedIn Post Generation (Compact)")
        
        if success_standard and success_compact:
            # Move to final directory
            final_standard = self.output_dir / self.run_id / "final" / "linkedin_post.txt"
            final_compact = self.output_dir / self.run_id / "final" / "linkedin_post_compact.txt"
            
            shutil.move(str(self.linkedin_post_file), str(final_standard))
            shutil.move(str(self.linkedin_compact_file), str(final_compact))
            
            self.linkedin_post_file = final_standard
            self.linkedin_compact_file = final_compact
            
        return success_standard and success_compact
    
    def create_summary_report(self):
        """Create a summary report of the pipeline run."""
        report_file = self.output_dir / self.run_id / "pipeline_summary.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("BIOTECH NEWS PIPELINE SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Run ID: {self.run_id}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Output Directory: {self.output_dir / self.run_id}\n\n")
            
            if self.date_range:
                f.write(f"Date Range: {self.date_range[0]} to {self.date_range[1]}\n\n")
            else:
                f.write("Date Range: Last 7 days (default)\n\n")
            
            f.write("GENERATED FILES:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Raw Articles: {self.articles_file}\n")
            f.write(f"Filtered Articles: {self.filtered_articles_file}\n")
            f.write(f"Podcast Script: {self.podcast_file}\n")
            f.write(f"LinkedIn Post (Standard): {self.linkedin_post_file}\n")
            f.write(f"LinkedIn Post (Compact): {self.linkedin_compact_file}\n")
            f.write(f"Pipeline Log: {self.pipeline_log_file}\n\n")
            
            f.write("DIRECTORY STRUCTURE:\n")
            f.write("-" * 20 + "\n")
            f.write("raw/ - Original RSS parsed articles\n")
            f.write("processed/ - Date-filtered articles\n")
            f.write("final/ - Podcast script and LinkedIn posts\n\n")
            
            f.write("NEXT STEPS:\n")
            f.write("-" * 20 + "\n")
            f.write("1. Review the podcast script in final/podcast_script.txt\n")
            f.write("2. Copy the LinkedIn post content from final/linkedin_post.txt\n")
            f.write("3. Post to LinkedIn with the generated content\n")
            f.write("4. Use the compact version if you prefer shorter posts\n")
        
        print(f"Pipeline summary saved to: {report_file}")
    
    def run_pipeline(self) -> bool:
        """Run the complete pipeline."""
        print(f"🚀 Starting Biotech News Pipeline - Run ID: {self.run_id}")
        print(f"📁 Output Directory: {self.output_dir / self.run_id}")
        print("=" * 60)
        
        # Initialize log file
        with open(self.pipeline_log_file, 'w', encoding='utf-8') as f:
            f.write(f"Biotech News Pipeline Log - Run ID: {self.run_id}\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
        
        # Run pipeline steps
        steps = [
            ("RSS Feed Parsing", self.step_1_parse_rss_feeds),
            ("Date Range Filtering", self.step_2_filter_by_date_range),
            ("Podcast Generation", self.step_3_generate_podcast),
            ("LinkedIn Post Creation", self.step_4_create_linkedin_posts)
        ]
        
        all_success = True
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}")
            print("-" * 40)
            
            success = step_func()
            if not success:
                all_success = False
                print(f"❌ Pipeline failed at step: {step_name}")
                break
        
        # Create summary report
        self.create_summary_report()
        
        # Final status
        print("\n" + "=" * 60)
        if all_success:
            print("🎉 Pipeline completed successfully!")
            print(f"📂 All files saved to: {self.output_dir / self.run_id}")
            print(f"📝 LinkedIn posts ready in: {self.output_dir / self.run_id / 'final'}")
        else:
            print("❌ Pipeline failed. Check the log file for details.")
        
        return all_success

def main():
    """Main function to handle command line arguments and execute the pipeline."""
    parser = argparse.ArgumentParser(
        description="Complete Biotech News Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py
  python pipeline.py --output my_output --start-date 2025-08-18 --end-date 2025-08-24
  python pipeline.py --output weekly_reports --days 7
        """
    )
    
    parser.add_argument('--output', '-o', default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--start-date', '-s', 
                       help='Start date for filtering (YYYY-MM-DD)')
    parser.add_argument('--end-date', '-e',
                       help='End date for filtering (YYYY-MM-DD)')
    parser.add_argument('--days', '-d', type=int,
                       help='Number of days to look back (default: 7)')
    
    args = parser.parse_args()
    
    # Determine date range
    date_range = None
    if args.start_date and args.end_date:
        date_range = (args.start_date, args.end_date)
    elif args.days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        date_range = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    # Initialize and run pipeline
    pipeline = BiotechPipeline(args.output, date_range)
    success = pipeline.run_pipeline()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
