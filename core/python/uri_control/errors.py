class UriControlError(Exception):
    """Base exception for uri_control."""


class UriParseError(UriControlError):
    """Raised when a URI cannot be parsed."""


class RegistryError(UriControlError):
    """Raised for invalid manifests or registry state."""


class RouteNotFoundError(UriControlError):
    """Raised when no route matches a URI."""


class HandlerLoadError(UriControlError):
    """Raised when a handler reference cannot be loaded."""


class PolicyDeniedError(UriControlError):
    """Raised when policy denies a command or query."""
