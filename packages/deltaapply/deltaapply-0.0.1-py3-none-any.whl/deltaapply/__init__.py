"""DeltaApply - Change Data Capture with automatic application of inserts, updates and deletes."""

from .core import DeltaApply
from .data_sources import DataSource
from .exceptions import DeltaApplyError, UnsupportedDataSourceError, CDCOperationError

__version__ = "0.0.1.dev0"
__all__ = ["DeltaApply", "DataSource", "DeltaApplyError", "UnsupportedDataSourceError", "CDCOperationError"]