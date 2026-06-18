"""Shim — implementation in ``uriresolver`` (module ``uri_resolver``). Optional ``[mesh]`` extra."""
import sys

try:
    import uri_resolver as _impl
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "uri_control.resolver requires the 'uriresolver' package — pip install 'uricontrol[mesh]'"
    ) from exc

sys.modules[__name__] = _impl
