"""Shim — implementation in ``uri_router.transport``."""
import sys

from uri_router import transport as _impl

sys.modules[__name__] = _impl
