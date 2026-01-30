"""Custom exceptions for Nexus."""


class NexusError(Exception):
    """Base exception for all Nexus errors."""

    pass


class ConfigError(NexusError):
    """Configuration-related errors."""

    pass


class StorageError(NexusError):
    """Storage operation errors."""

    pass


class IngestionError(NexusError):
    """Content ingestion errors."""

    pass


class SearchError(NexusError):
    """Search operation errors."""

    pass


class SourceNotFoundError(NexusError):
    """Requested source does not exist."""

    pass
