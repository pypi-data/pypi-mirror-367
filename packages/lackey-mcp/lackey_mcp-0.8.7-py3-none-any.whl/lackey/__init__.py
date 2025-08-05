"""Lackey - Task chain management engine for AI agents."""

import logging

from .core import LackeyCore
from .dependencies import (
    CircularDependencyError,
    DependencyError,
    DependencyValidator,
    dependency_validator,
)
from .file_ops import (
    FileOperationError,
    IntegrityError,
    TransactionError,
    TransactionManager,
    atomic_write,
)
from .models import (
    Complexity,
    LackeyConfig,
    Project,
    ProjectIndex,
    ProjectStatus,
    Task,
    TaskStatus,
)
from .storage import (
    LackeyStorage,
    ProjectNotFoundError,
    StorageError,
    TaskNotFoundError,
)
from .validation import InputValidator, SecurityError, ValidationError, validator

__version__ = "0.8.7"
__author__ = "Lackey Contributors"
__email__ = "contact@lackey.dev"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

__all__ = [
    # Core classes
    "LackeyCore",
    "LackeyStorage",
    # Models
    "Task",
    "Project",
    "ProjectIndex",
    "LackeyConfig",
    "TaskStatus",
    "Complexity",
    "ProjectStatus",
    # Validators
    "dependency_validator",
    "DependencyValidator",
    "validator",
    "InputValidator",
    # File operations
    "atomic_write",
    "TransactionManager",
    # Exceptions
    "ValidationError",
    "SecurityError",
    "FileOperationError",
    "IntegrityError",
    "TransactionError",
    "DependencyError",
    "CircularDependencyError",
    "StorageError",
    "TaskNotFoundError",
    "ProjectNotFoundError",
]
