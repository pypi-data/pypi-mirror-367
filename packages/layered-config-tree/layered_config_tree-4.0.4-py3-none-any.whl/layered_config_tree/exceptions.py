from typing import Any


class ConfigurationError(Exception):
    """Base class for configuration errors."""

    def __init__(self, message: str, value_name: str | None = None):
        super().__init__(message)
        self.value_name = value_name


class ConfigurationKeyError(ConfigurationError, KeyError):
    """Error raised when a configuration lookup fails."""

    pass


class MissingLayerError(ConfigurationError):
    """Error raised when values exist but not at the explicitly-requested layer."""

    pass


class ImproperAccessError(ConfigurationError):
    """Error raised when a configuration value is accessed improperly."""

    pass


class DuplicatedConfigurationError(ConfigurationError):
    """Error raised when a configuration value is set more than once.

    Attributes
    ----------
    layer
        The configuration layer at which the value is being set.
    source
        The original source of the configuration value.
    value
        The original configuration value.

    """

    def __init__(
        self,
        message: str,
        name: str,
        layer: str | None,
        source: str | None,
        value: Any,
    ):
        self.layer = layer
        self.source = source
        self.value = value
        super().__init__(message, name)
