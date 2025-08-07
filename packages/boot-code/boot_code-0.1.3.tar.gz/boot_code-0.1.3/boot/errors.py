class SpexError(Exception):
    """Base exception for all application-specific errors."""

    pass


class GenerationError(SpexError):
    """Raised when there is an error during the code generation process."""

    pass


class SpecValidationError(SpexError):
    """Raised when a specification file fails validation."""

    pass


class ConfigError(SpexError):
    """Raised for configuration-related errors."""

    pass
