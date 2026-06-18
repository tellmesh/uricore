"""Shim — implementation in ``uri_router.resolver``."""
import sys

from uri_router import resolver as _impl

sys.modules[__name__] = _impl
