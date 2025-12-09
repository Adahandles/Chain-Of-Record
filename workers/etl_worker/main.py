# ETL Worker main process
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.ingest.base import IngestCoordinator
from app.ingest.sunbiz import SunbizSource
from app.ingest.property_appraiser_fl_marion import MarionCountyPropertySource
import time


def setup_worker():
    """Initialize worker environment."""
    setup_logging()
    logger = get_logger(__name__)
    logger.info("ETL Worker starting up")
    return logger


def create_coordinator(db: Session) -> IngestCoordinator:
    """Create and configure the ingest coordinator."""
    coordinator = IngestCoordinator(db)
    
    # Register data sources
    coordinator.register_source(SunbizSource())
    coordinator.register_source(MarionCountyPropertySource())
    
    return coordinator


def run_full_ingest(logger):
    """Run complete ingest process for all sources."""
    db: Session = SessionLocal()
    
    try:
        coordinator = create_coordinator(db)
        
        logger.info("Starting full ingest process")
        start_time = time.time()
        
        # Run all sources
        results = coordinator.run_all_sources(batch_size=50, max_errors=5)
        
        # Log results
        total_processed = 0
        total_successful = 0
        total_failed = 0
        
        for source_name, result in results.items():
            logger.info(
                f"Source {source_name}: {result.status.value} - "
                f"{result.records_successful}/{result.records_processed} successful "
                f"({result.success_rate:.1f}%) in {result.duration_seconds:.2f}s"
            )
            
            total_processed += result.records_processed
            total_successful += result.records_successful
            total_failed += result.records_failed
            
            if result.errors:
                logger.warning(f"Errors in {source_name}: {result.errors[:3]}")  # Show first 3 errors
        
        total_time = time.time() - start_time
        
        logger.info(
            f"Full ingest complete: {total_successful}/{total_processed} successful "
            f"({(total_successful/total_processed*100):.1f}%) in {total_time:.2f}s"
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Fatal error in ingest process: {e}")
        raise
    finally:
        db.close()


def run_single_source(source_name: str, logger, **kwargs):
    """Run ingest for a single source."""
    db: Session = SessionLocal()
    
    try:
        coordinator = create_coordinator(db)
        
        logger.info(f"Running ingest for source: {source_name}")
        
        result = coordinator.run_source(source_name, **kwargs)
        
        logger.info(
            f"Source {source_name} complete: {result.status.value} - "
            f"{result.records_successful}/{result.records_processed} successful "
            f"({result.success_rate:.1f}%) in {result.duration_seconds:.2f}s"
        )
        
        if result.errors:
            logger.warning(f"Errors: {result.errors}")
        
        return result
        
    finally:
        db.close()


def main():
    """Main worker entry point."""
    logger = setup_worker()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "full":
            run_full_ingest(logger)
        elif command == "sunbiz":
            run_single_source("sunbiz", logger)
        elif command == "marion":
            run_single_source("marion_pa", logger)
        else:
            logger.error(f"Unknown command: {command}")
            print("Usage: python main.py [full|sunbiz|marion]")
            sys.exit(1)
    else:
        # Default: run full ingest
        run_full_ingest(logger)


if __name__ == "__main__":
    main()