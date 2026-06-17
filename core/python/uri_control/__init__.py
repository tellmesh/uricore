"""uricore Python runtime module.

The Python distribution is named ``uricore``. The importable runtime module is
``uri_control`` to keep the API descriptive and language-neutral.
"""

from .dispatcher import UriControlRuntime
from .event_store import EventStore, InMemoryEventStore, JsonlEventStore
from .handlers import load_handler, load_python_handler, make_remote_handler
from .models import (
    CapabilityManifest,
    DispatchResult,
    EventEnvelope,
    ParsedUri,
    PolicyDecision,
    Route,
)
from .parser import parse_uri
from .policy import PolicyEngine
from .projection import ProjectionBuilder
from .registry import CapabilityRegistry

__all__ = [
    "CapabilityManifest",
    "CapabilityRegistry",
    "DispatchResult",
    "EventEnvelope",
    "EventStore",
    "InMemoryEventStore",
    "JsonlEventStore",
    "load_handler",
    "load_python_handler",
    "make_remote_handler",
    "ParsedUri",
    "PolicyDecision",
    "PolicyEngine",
    "ProjectionBuilder",
    "Route",
    "UriControlRuntime",
    "parse_uri",
]
