# ETL Worker scheduler for automated runs
import schedule
import time
import sys
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.logging import setup_logging, get_logger
from .main import run_full_ingest, run_single_source


class ETLScheduler:
    """
    Scheduler for ETL jobs.
    Manages automated data ingestion on configurable schedules.
    """
    
    def __init__(self):
        setup_logging()
        self.logger = get_logger(__name__)
        self.setup_jobs()
    
    def setup_jobs(self):
        """Configure scheduled jobs."""
        
        # Full ingest daily at 2 AM
        schedule.every().day.at("02:00").do(self.run_daily_full_ingest)
        
        # Sunbiz updates every 4 hours during business hours
        schedule.every(4).hours.do(self.run_sunbiz_update).tag("business_hours")
        
        # Marion County updates twice daily
        schedule.every().day.at("06:00").do(self.run_marion_update)
        schedule.every().day.at("18:00").do(self.run_marion_update)
        
        self.logger.info("ETL jobs scheduled")
        self.logger.info("- Full ingest: Daily at 2:00 AM")
        self.logger.info("- Sunbiz updates: Every 4 hours")  
        self.logger.info("- Marion updates: 6:00 AM and 6:00 PM")
    
    def run_daily_full_ingest(self):
        """Run the full daily ingest."""
        self.logger.info("Starting scheduled full ingest")
        try:
            run_full_ingest(self.logger)
            self.logger.info("Scheduled full ingest completed successfully")
        except Exception as e:
            self.logger.error(f"Scheduled full ingest failed: {e}")
    
    def run_sunbiz_update(self):
        """Run Sunbiz incremental update."""
        # Only run during business hours (8 AM - 8 PM)
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 20:
            self.logger.info("Starting scheduled Sunbiz update")
            try:
                run_single_source("sunbiz", self.logger, batch_size=100)
                self.logger.info("Scheduled Sunbiz update completed")
            except Exception as e:
                self.logger.error(f"Scheduled Sunbiz update failed: {e}")
        else:
            self.logger.debug("Skipping Sunbiz update (outside business hours)")
    
    def run_marion_update(self):
        """Run Marion County update.""" 
        self.logger.info("Starting scheduled Marion County update")
        try:
            run_single_source("marion_pa", self.logger, batch_size=200)
            self.logger.info("Scheduled Marion County update completed")
        except Exception as e:
            self.logger.error(f"Scheduled Marion County update failed: {e}")
    
    def run_scheduler(self):
        """Run the scheduler loop."""
        self.logger.info("ETL Scheduler started")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("ETL Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"ETL Scheduler error: {e}")
    
    def list_jobs(self):
        """List all scheduled jobs."""
        jobs = schedule.get_jobs()
        self.logger.info(f"Scheduled jobs ({len(jobs)} total):")
        
        for job in jobs:
            self.logger.info(f"- {job.job_func.__name__}: {job.next_run}")
    
    def run_job_now(self, job_name: str):
        """Run a specific job immediately."""
        job_map = {
            "full": self.run_daily_full_ingest,
            "sunbiz": self.run_sunbiz_update,
            "marion": self.run_marion_update
        }
        
        if job_name in job_map:
            self.logger.info(f"Running job immediately: {job_name}")
            job_map[job_name]()
        else:
            self.logger.error(f"Unknown job: {job_name}")
            self.logger.info(f"Available jobs: {list(job_map.keys())}")


def main():
    """Scheduler main entry point."""
    scheduler = ETLScheduler()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            scheduler.run_scheduler()
        elif command == "list":
            scheduler.list_jobs()
        elif command in ["full", "sunbiz", "marion"]:
            scheduler.run_job_now(command)
        else:
            print("Usage: python scheduler.py [start|list|full|sunbiz|marion]")
            print("  start  - Run the scheduler daemon")
            print("  list   - List scheduled jobs")
            print("  full   - Run full ingest now")
            print("  sunbiz - Run Sunbiz update now")
            print("  marion - Run Marion update now")
            sys.exit(1)
    else:
        # Default: show help
        print("ETL Scheduler")
        print("Usage: python scheduler.py [start|list|full|sunbiz|marion]")


if __name__ == "__main__":
    main()