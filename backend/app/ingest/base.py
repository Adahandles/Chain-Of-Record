# Abstract base classes for ETL ingestion
from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session
from app.core.logging import get_logger

logger = get_logger(__name__)


class IngestStatus(Enum):
    """Status of an ingest operation."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class IngestResult:
    """Result of an ingest operation."""
    status: IngestStatus
    records_processed: int
    records_successful: int
    records_failed: int
    errors: List[str]
    duration_seconds: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.records_processed == 0:
            return 0.0
        return (self.records_successful / self.records_processed) * 100


class RawRecord(dict):
    """
    Wrapper for raw scraped/API data.
    Inherits from dict for easy access while adding metadata.
    """
    
    def __init__(self, data: Dict[str, Any], source_url: Optional[str] = None):
        super().__init__(data)
        self.source_url = source_url
        self.ingested_at = None


class NormalizedRecord(dict):
    """
    Wrapper for normalized data ready for database persistence.
    """
    
    def __init__(self, data: Dict[str, Any], source_system: str, record_type: str):
        super().__init__(data)
        self.source_system = source_system
        self.record_type = record_type  # 'entity', 'property', 'relationship'


class IngestSource(ABC):
    """
    Abstract base class for all data ingestion sources.
    Each concrete implementation handles one data source (e.g., Sunbiz, County Appraiser).
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"ingest.{name}")
    
    @abstractmethod
    def fetch_batch(self, batch_size: int = 100, **kwargs) -> Iterable[RawRecord]:
        """
        Fetch a batch of raw records from the source.
        
        Args:
            batch_size: Maximum number of records to fetch
            **kwargs: Source-specific parameters
            
        Yields:
            RawRecord: Raw data from the source
        """
        pass
    
    @abstractmethod
    def normalize(self, raw: RawRecord) -> List[NormalizedRecord]:
        """
        Normalize a raw record into one or more normalized records.
        
        Args:
            raw: Raw record from fetch_batch
            
        Returns:
            List of normalized records ready for persistence
        """
        pass
    
    @abstractmethod
    def persist(self, normalized_records: List[NormalizedRecord], db: Session) -> int:
        """
        Persist normalized records to the database.
        
        Args:
            normalized_records: List of normalized records
            db: Database session
            
        Returns:
            Number of records successfully persisted
        """
        pass
    
    def validate_raw_record(self, raw: RawRecord) -> bool:
        """
        Validate a raw record before normalization.
        Override in subclasses for source-specific validation.
        
        Args:
            raw: Raw record to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def get_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Get the current ingestion checkpoint for incremental loading.
        Override in subclasses that support incremental ingestion.
        
        Returns:
            Checkpoint data or None for full refresh
        """
        return None
    
    def save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """
        Save the current ingestion checkpoint.
        Override in subclasses that support incremental ingestion.
        
        Args:
            checkpoint: Checkpoint data to save
        """
        pass


class BatchProcessor:
    """
    Generic batch processor for running ingest sources.
    Handles error recovery, logging, and metrics collection.
    """
    
    def __init__(self, source: IngestSource, db: Session):
        self.source = source
        self.db = db
        self.logger = get_logger(f"batch.{source.name}")
    
    def process_batch(
        self,
        batch_size: int = 100,
        max_errors: int = 10,
        **fetch_kwargs
    ) -> IngestResult:
        """
        Process a full batch from the source.
        
        Args:
            batch_size: Size of batches to process
            max_errors: Maximum errors before stopping
            **fetch_kwargs: Passed to source.fetch_batch
            
        Returns:
            IngestResult with processing statistics
        """
        import time
        
        start_time = time.time()
        records_processed = 0
        records_successful = 0
        records_failed = 0
        errors = []
        
        try:
            self.logger.info(f"Starting batch processing for {self.source.name}")
            
            for raw_record in self.source.fetch_batch(batch_size, **fetch_kwargs):
                records_processed += 1
                
                try:
                    # Validate raw record
                    if not self.source.validate_raw_record(raw_record):
                        records_failed += 1
                        errors.append(f"Record {records_processed}: Validation failed")
                        continue
                    
                    # Normalize record
                    normalized_records = self.source.normalize(raw_record)
                    
                    if not normalized_records:
                        records_failed += 1
                        errors.append(f"Record {records_processed}: Normalization produced no records")
                        continue
                    
                    # Persist records
                    persisted_count = self.source.persist(normalized_records, self.db)
                    
                    if persisted_count > 0:
                        records_successful += persisted_count
                        self.db.commit()
                    else:
                        records_failed += 1
                        errors.append(f"Record {records_processed}: Persistence failed")
                        self.db.rollback()
                
                except Exception as e:
                    records_failed += 1
                    error_msg = f"Record {records_processed}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
                    
                    # Stop if too many errors
                    if len(errors) >= max_errors:
                        self.logger.error(f"Stopping due to {len(errors)} errors")
                        break
                    
                    self.db.rollback()
        
        except Exception as e:
            self.logger.error(f"Fatal error in batch processing: {e}")
            errors.append(f"Fatal error: {str(e)}")
            status = IngestStatus.FAILURE
        else:
            # Determine status
            if records_failed == 0:
                status = IngestStatus.SUCCESS
            elif records_successful == 0:
                status = IngestStatus.FAILURE
            else:
                status = IngestStatus.PARTIAL
        
        duration = time.time() - start_time
        
        result = IngestResult(
            status=status,
            records_processed=records_processed,
            records_successful=records_successful,
            records_failed=records_failed,
            errors=errors,
            duration_seconds=duration
        )
        
        self.logger.info(
            f"Batch processing complete: {records_successful}/{records_processed} successful "
            f"({result.success_rate:.1f}%) in {duration:.2f}s"
        )
        
        return result


class IngestCoordinator:
    """
    Coordinates multiple ingest sources and manages scheduling.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.sources: Dict[str, IngestSource] = {}
        self.logger = get_logger("ingest.coordinator")
    
    def register_source(self, source: IngestSource) -> None:
        """Register an ingest source."""
        self.sources[source.name] = source
        self.logger.info(f"Registered ingest source: {source.name}")
    
    def run_source(self, source_name: str, **kwargs) -> IngestResult:
        """Run a specific ingest source."""
        if source_name not in self.sources:
            raise ValueError(f"Unknown source: {source_name}")
        
        source = self.sources[source_name]
        processor = BatchProcessor(source, self.db)
        
        return processor.process_batch(**kwargs)
    
    def run_all_sources(self, **kwargs) -> Dict[str, IngestResult]:
        """Run all registered sources."""
        results = {}
        
        for source_name in self.sources:
            self.logger.info(f"Running source: {source_name}")
            try:
                results[source_name] = self.run_source(source_name, **kwargs)
            except Exception as e:
                self.logger.error(f"Error running source {source_name}: {e}")
                results[source_name] = IngestResult(
                    status=IngestStatus.FAILURE,
                    records_processed=0,
                    records_successful=0,
                    records_failed=0,
                    errors=[str(e)],
                    duration_seconds=0
                )
        
        return results
    
    def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status information for all sources."""
        status = {}
        
        for name, source in self.sources.items():
            status[name] = {
                "name": source.name,
                "description": source.description,
                "checkpoint": source.get_checkpoint()
            }
        
        return status