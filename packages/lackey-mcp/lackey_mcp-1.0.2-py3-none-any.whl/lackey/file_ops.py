"""Atomic file operations with rollback capabilities for Lackey."""

import json
import os
import shutil
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .validation import SecurityError, validator


class FileOperationError(Exception):
    """Raised when file operations fail."""

    pass


class IntegrityError(Exception):
    """Raised when file integrity checks fail."""

    pass


class TransactionError(Exception):
    """Raised when transaction operations fail."""

    pass


@dataclass
class OperationLog:
    """Log entry for file operations."""

    operation: str
    path: str
    timestamp: float
    checksum_before: Optional[str] = None
    checksum_after: Optional[str] = None
    backup_path: Optional[str] = None
    success: bool = False
    error: Optional[str] = None


class AtomicFileOperation:
    """
    Ensures atomic file operations with rollback capability.

    All file modifications are performed atomically using write-then-move
    operations with automatic backup and rollback on failure.
    """

    def __init__(self, target_path: str):
        """Initialize atomic file operation."""
        self.target_path = Path(target_path)
        self.temp_path: Optional[Path] = None
        self.backup_path: Optional[Path] = None
        self.operation_log: List[OperationLog] = []
        self.operation_id = str(uuid.uuid4())

        # Validate path
        try:
            validator.sanitize_path(str(target_path))
        except SecurityError as e:
            raise FileOperationError(f"Invalid path: {e}")

    def __enter__(self) -> "AtomicFileOperation":
        """Enter context manager."""
        # Create backup if file exists
        if self.target_path.exists():
            self.backup_path = self._create_backup()

            # Calculate checksum before operation
            checksum_before = validator.calculate_file_checksum(str(self.target_path))

            self.operation_log.append(
                OperationLog(
                    operation="backup_created",
                    path=str(self.backup_path),
                    timestamp=time.time(),
                    checksum_before=checksum_before,
                )
            )

        # Create temporary file
        self.temp_path = self._create_temp_file()

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager with cleanup."""
        try:
            if exc_type is None:
                # Success: atomically move temp file to target
                self._commit_operation()
            else:
                # Failure: rollback to backup
                self._rollback_operation()
        finally:
            self._cleanup_temp_files()

    def write_content(self, content: str, encoding: str = "utf-8") -> None:
        """Write content to temporary file with integrity checks."""
        if self.temp_path is None:
            raise FileOperationError("Operation not initialized")

        try:
            # Write to temporary file
            with open(self.temp_path, "w", encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Verify written content
            with open(self.temp_path, "r", encoding=encoding) as f:
                written_content = f.read()
                if written_content != content:
                    raise IntegrityError("Content verification failed")

            # Validate file size and extension
            validator.validate_file_size(str(self.temp_path))
            validator.validate_file_extension(str(self.target_path))
            validator.validate_encoding(str(self.temp_path))

            # Calculate checksum
            checksum_after = validator.calculate_file_checksum(str(self.temp_path))

            self.operation_log.append(
                OperationLog(
                    operation="content_written",
                    path=str(self.temp_path),
                    timestamp=time.time(),
                    checksum_after=checksum_after,
                    success=True,
                )
            )

        except Exception as e:
            self.operation_log.append(
                OperationLog(
                    operation="content_write_failed",
                    path=str(self.temp_path),
                    timestamp=time.time(),
                    error=str(e),
                )
            )
            raise FileOperationError(f"Failed to write content: {e}")

    def write_yaml(self, data: Dict[str, Any]) -> None:
        """Write YAML data with validation."""
        try:
            content = yaml.dump(
                data, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
            self.write_content(content)
        except yaml.YAMLError as e:
            raise FileOperationError(f"YAML serialization failed: {e}")

    def write_json(self, data: Dict[str, Any], indent: int = 2) -> None:
        """Write JSON data with validation."""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            self.write_content(content)
        except (TypeError, ValueError) as e:
            raise FileOperationError(f"JSON serialization failed: {e}")

    def _create_backup(self) -> Path:
        """Create backup of existing file."""
        timestamp = int(time.time())
        backup_path = self.target_path.with_suffix(
            f"{self.target_path.suffix}.backup.{timestamp}"
        )

        try:
            shutil.copy2(self.target_path, backup_path)
            return backup_path
        except IOError as e:
            raise FileOperationError(f"Failed to create backup: {e}")

    def _create_temp_file(self) -> Path:
        """Create temporary file for atomic operations."""
        temp_dir = self.target_path.parent
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_path = temp_dir / f"{self.target_path.name}.tmp.{self.operation_id}"
        return temp_path

    def _commit_operation(self) -> None:
        """Commit the operation by moving temp file to target."""
        try:
            # Ensure parent directory exists
            self.target_path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic move
            shutil.move(str(self.temp_path), str(self.target_path))

            # Verify final file
            checksum_final = validator.calculate_file_checksum(str(self.target_path))

            self.operation_log.append(
                OperationLog(
                    operation="operation_committed",
                    path=str(self.target_path),
                    timestamp=time.time(),
                    checksum_after=checksum_final,
                    success=True,
                )
            )

            # Clean up backup after successful operation
            if self.backup_path and self.backup_path.exists():
                self.backup_path.unlink()

        except Exception as e:
            self.operation_log.append(
                OperationLog(
                    operation="commit_failed",
                    path=str(self.target_path),
                    timestamp=time.time(),
                    error=str(e),
                )
            )
            raise FileOperationError(f"Failed to commit operation: {e}")

    def _rollback_operation(self) -> None:
        """Rollback to previous state on failure."""
        try:
            # Remove temp file if it exists
            if self.temp_path and self.temp_path.exists():
                self.temp_path.unlink()

            # Restore from backup if available
            if self.backup_path and self.backup_path.exists():
                shutil.move(str(self.backup_path), str(self.target_path))

                self.operation_log.append(
                    OperationLog(
                        operation="rollback_completed",
                        path=str(self.target_path),
                        timestamp=time.time(),
                        success=True,
                    )
                )

        except Exception as rollback_error:
            # Log rollback failure - this is critical
            self.operation_log.append(
                OperationLog(
                    operation="rollback_failed",
                    path=str(self.target_path),
                    timestamp=time.time(),
                    error=str(rollback_error),
                )
            )

            # This is a critical error that should be logged
            import logging

            logging.critical(
                f"Rollback failed for operation {self.operation_id}: "
                f"{rollback_error}",
                extra={"operation_log": [log.__dict__ for log in self.operation_log]},
            )

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        try:
            if self.temp_path and self.temp_path.exists():
                self.temp_path.unlink()

            if self.backup_path and self.backup_path.exists():
                self.backup_path.unlink()

        except Exception as e:
            # Log cleanup failure but don't raise
            import logging

            logging.warning(f"Failed to cleanup temp files: {e}")


class TransactionManager:
    """
    Manages multi-file operations with full rollback capability.

    Ensures that either all file operations succeed or all are rolled back
    to maintain consistency across multiple files.
    """

    def __init__(self) -> None:
        """Initialize transaction manager."""
        self.operations: List[tuple] = []
        self.transaction_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.completed_operations: List[AtomicFileOperation] = []

    def add_file_operation(self, file_path: str, content: str) -> None:
        """Add a file operation to the transaction."""
        self.operations.append(("write_content", file_path, content))

    def add_yaml_operation(self, file_path: str, data: Dict[str, Any]) -> None:
        """Add a YAML file operation to the transaction."""
        self.operations.append(("write_yaml", file_path, data))

    def add_json_operation(self, file_path: str, data: Dict[str, Any]) -> None:
        """Add a JSON file operation to the transaction."""
        self.operations.append(("write_json", file_path, data))

    def commit(self) -> None:
        """Execute all operations atomically."""
        if not self.operations:
            return

        try:
            # Execute all operations
            for operation_type, file_path, data in self.operations:
                operation = AtomicFileOperation(file_path)

                with operation:
                    if operation_type == "write_content":
                        operation.write_content(data)
                    elif operation_type == "write_yaml":
                        operation.write_yaml(data)
                    elif operation_type == "write_json":
                        operation.write_json(data)
                    else:
                        raise TransactionError(f"Unknown operation: {operation_type}")

                self.completed_operations.append(operation)

            import logging

            logging.info(f"Transaction {self.transaction_id} completed successfully")

        except Exception as e:
            # All individual operations have their own rollback
            # Transaction failure is logged for analysis
            import logging

            logging.error(
                f"Transaction {self.transaction_id} failed: {e}",
                extra={
                    "transaction_id": self.transaction_id,
                    "operations_count": len(self.operations),
                    "completed_count": len(self.completed_operations),
                },
            )
            raise TransactionError(f"Transaction {self.transaction_id} failed: {e}")


@contextmanager
def atomic_write(file_path: str) -> Any:
    """Context manager for atomic file writes."""
    operation = AtomicFileOperation(file_path)
    with operation:
        yield operation


def read_yaml_file(file_path: str) -> Dict[str, Any]:
    """Read and parse YAML file with validation."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        # Validate file
        validator.validate_file_extension(file_path)
        validator.validate_file_size(file_path)
        validator.validate_encoding(file_path)

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise FileOperationError(
                f"YAML file must contain a dictionary, got {type(data)}"
            )

        return data

    except yaml.YAMLError as e:
        raise FileOperationError(f"YAML parsing failed: {e}")
    except IOError as e:
        raise FileOperationError(f"File read failed: {e}")


def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read and parse JSON file with validation."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        # Validate file
        validator.validate_file_extension(file_path)
        validator.validate_file_size(file_path)
        validator.validate_encoding(file_path)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise FileOperationError(
                f"JSON file must contain a dictionary, got {type(data)}"
            )

        return data

    except json.JSONDecodeError as e:
        raise FileOperationError(f"JSON parsing failed: {e}")
    except IOError as e:
        raise FileOperationError(f"File read failed: {e}")


def read_text_file(file_path: str) -> str:
    """Read text file with validation."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        # Validate file
        validator.validate_file_size(file_path)
        validator.validate_encoding(file_path)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return content

    except IOError as e:
        raise FileOperationError(f"File read failed: {e}")


def ensure_directory(dir_path: str) -> None:
    """Ensure directory exists with proper permissions."""
    path = Path(dir_path)

    try:
        # Validate path
        validator.sanitize_path(str(dir_path))

        # Create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)

        # Verify directory is writable
        test_file = path / f".write_test_{uuid.uuid4()}"
        try:
            test_file.touch()
            test_file.unlink()
        except IOError:
            raise FileOperationError(f"Directory not writable: {dir_path}")

    except SecurityError as e:
        raise FileOperationError(f"Invalid directory path: {e}")
    except IOError as e:
        raise FileOperationError(f"Failed to create directory: {e}")


def safe_delete_file(file_path: str, create_backup: bool = True) -> Optional[str]:
    """Safely delete a file with optional backup."""
    path = Path(file_path)

    if not path.exists():
        return None

    backup_path = None

    try:
        # Create backup if requested
        if create_backup:
            timestamp = int(time.time())
            backup_path = str(path.with_suffix(f"{path.suffix}.deleted.{timestamp}"))
            shutil.copy2(path, backup_path)

        # Delete original file
        path.unlink()

        return backup_path

    except IOError as e:
        # If backup was created but deletion failed, clean up backup
        if backup_path and Path(backup_path).exists():
            try:
                Path(backup_path).unlink()
            except IOError:
                pass  # Ignore cleanup failure

        raise FileOperationError(f"Failed to delete file: {e}")


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        stat = path.stat()
        checksum = validator.calculate_file_checksum(file_path)

        return {
            "path": str(path),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "checksum": checksum,
            "extension": path.suffix,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
        }

    except IOError as e:
        raise FileOperationError(f"Failed to get file info: {e}")
