from __future__ import annotations


class ModemBridgeError(Exception):
    """Base exception for ModemBridge."""


class ModemConfigurationError(ModemBridgeError):
    """Raised when the provided modem profile is invalid."""


class DriverNotFoundError(ModemBridgeError):
    """Raised when no registered driver matches the requested profile."""


class ModemAuthenticationError(ModemBridgeError):
    """Raised when driver authentication fails."""


class SmsSendError(ModemBridgeError):
    """Raised when SMS sending fails irrecoverably."""
