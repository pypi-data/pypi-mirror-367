"""Custom exceptions for DeltaApply."""


class DeltaApplyError(Exception):
    """Base exception for all DeltaApply errors."""
    pass


class UnsupportedDataSourceError(DeltaApplyError):
    """Raised when an unsupported data source type is provided."""
    pass


class CDCOperationError(DeltaApplyError):
    """Raised when a CDC operation fails."""
    pass