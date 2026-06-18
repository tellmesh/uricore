"""Shim — implementation in ``uritransport`` (module ``uri_transport``). Optional ``[mesh]`` extra."""
import sys

try:
    import uri_transport as _impl
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "uri_control.transport requires the 'uritransport' package — pip install 'uricontrol[mesh]'"
    ) from exc

sys.modules[__name__] = _impl
