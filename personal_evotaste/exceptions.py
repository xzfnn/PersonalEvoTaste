"""Custom exception hierarchy for PersonalEvoTaste."""
from __future__ import annotations


class PersonalEvoTasteError(Exception):
    """Base exception for all PersonalEvoTaste errors."""


class StorageError(PersonalEvoTasteError):
    """Raised when the underlying memory storage fails."""


class ExtractionError(PersonalEvoTasteError):
    """Raised when a rule extractor fails to produce a rule."""


class ConfigurationError(PersonalEvoTasteError):
    """Raised when invalid configuration is supplied."""
