"""Shim — implementation in ``uri_router.envelope``."""
import sys

from uri_router import envelope as _impl

sys.modules[__name__] = _impl
