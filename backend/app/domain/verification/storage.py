# File storage utilities for verification documents
import os
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileStorage:
    """
    File storage utility for verification documents.
    Handles secure file storage with encryption support.
    """

    def __init__(self, base_path: str = "/tmp/verification_files"):
        """Initialize file storage with base path."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"File storage initialized at: {self.base_path}")

    def save_file(
        self,
        file_content: BinaryIO,
        verification_id: int,
        file_name: str,
        document_type: str,
        encrypt: bool = True
    ) -> tuple[str, int]:
        """
        Save a file to storage.
        
        Args:
            file_content: File content as binary stream
            verification_id: Verification request ID
            file_name: Original file name
            document_type: Type of document
            encrypt: Whether to encrypt the file (default: True)
            
        Returns:
            Tuple of (file_path, file_size)
        """
        # Create directory structure: base_path/verification_id/document_type/
        storage_dir = self.base_path / str(verification_id) / document_type
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file_name).suffix
        unique_filename = f"{timestamp}_{file_name}"
        file_path = storage_dir / unique_filename

        # Save file
        file_size = 0
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file_content, f)
            file_size = file_path.stat().st_size

        # TODO: Implement AES-256 encryption for secure file storage
        # Encryption implementation plan:
        # 1. Generate or retrieve encryption key from secure key management system
        # 2. Use cryptography.fernet or AES from cryptography.hazmat
        # 3. Encrypt file content before writing to disk
        # 4. Store encryption metadata (IV, key ID) in database
        # 5. Implement decryption for file retrieval
        # For now, files are stored unencrypted with encryption flag tracked
        if encrypt:
            # Placeholder for encryption logic
            logger.info(f"File saved (encryption to be implemented): {file_path}")
        else:
            logger.info(f"File saved without encryption: {file_path}")

        return str(file_path), file_size

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    def delete_verification_files(self, verification_id: int) -> bool:
        """
        Delete all files for a verification request.
        
        Args:
            verification_id: Verification request ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            verification_dir = self.base_path / str(verification_id)
            if verification_dir.exists():
                shutil.rmtree(verification_dir)
                logger.info(f"All files deleted for verification ID: {verification_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting verification files {verification_id}: {e}")
            return False

    def get_file_path(self, verification_id: int, document_type: str, file_name: str) -> Optional[Path]:
        """
        Get the full path to a file.
        
        Args:
            verification_id: Verification request ID
            document_type: Type of document
            file_name: File name
            
        Returns:
            Path to the file or None if not found
        """
        file_path = self.base_path / str(verification_id) / document_type / file_name
        if file_path.exists():
            return file_path
        return None

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()


# Global instance
file_storage = FileStorage()
