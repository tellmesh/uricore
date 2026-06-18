"""Resolver transport delegation — remote URI execution via HTTP/MQTT bridges.

When ``target_profile.transport`` is not ``local``, ``Runtime.call`` can forward
the envelope without matching a local route. Bridges are explicit (no hidden network):

* ``http`` — ``POST {endpoint}`` with ``{uri, payload, context}`` (urisys wire ABI)
* ``mqtt`` — ``POST {options.bridge_url}`` with ``{topic, uri, payload, context, qos}``
* ``ssh`` — alias when ``endpoint`` is an ``http(s)://`` remote urisys node

Env fallbacks: ``URISYS_HTTP_BRIDGE``, ``URISYS_MQTT_BRIDGE_URL``.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from typing import Any, Callable
from urllib import request

LOCAL_TRANSPORTS = frozenset({"", "local"})

# Test seam: when set, native MQTT request/response is routed here instead of
# opening a real broker connection. Signature:
#   hook(*, broker, pub_topic, sub_topic, body, timeout) -> dict
MQTT_REQUEST_HOOK: Callable[..., dict[str, Any]] | None = None


def _options(profile: dict[str, Any]) -> dict[str, Any]:
    raw = profile.get("options") or {}
    return dict(raw) if isinstance(raw, dict) else {}


def normalize_http_endpoint(profile: dict[str, Any]) -> str:
    endpoint = str(profile.get("endpoint") or profile.get("url") or "").strip()
    options = _options(profile)
    base = str(
        options.get("base_url")
        or os.environ.get("URISYS_HTTP_BRIDGE")
        or ""
    ).strip().rstrip("/")
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    if base and endpoint:
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{base}{path}"
    if base:
        return f"{base}/uri/call"
    raise ValueError("http transport requires endpoint URL or options.base_url / URISYS_HTTP_BRIDGE")


def mqtt_bridge_url(profile: dict[str, Any]) -> str | None:
    options = _options(profile)
    url = str(options.get("bridge_url") or "").strip()
    return url or os.environ.get("URISYS_MQTT_BRIDGE_URL", "").strip() or None


def mqtt_broker_url(profile: dict[str, Any]) -> str | None:
    """Native MQTT broker URL (``tcp://host:port``) from options/env, if any."""
    options = _options(profile)
    url = str(options.get("broker") or "").strip()
    return url or os.environ.get("URISYS_MQTT_BROKER", "").strip() or None


def mqtt_available() -> bool:
    if MQTT_REQUEST_HOOK is not None:
        return True
    try:  # pragma: no cover - depends on environment
        import paho.mqtt.client  # noqa: F401

        return True
    except Exception:  # pragma: no cover
        return False


def _parse_broker(broker: str) -> tuple[str, int]:
    """Parse ``tcp://host:port`` / ``host:port`` / ``host`` into ``(host, port)``."""
    raw = broker.strip()
    for prefix in ("tcp://", "mqtt://", "ssl://", "mqtts://"):
        if raw.startswith(prefix):
            raw = raw[len(prefix) :]
            break
    raw = raw.rstrip("/")
    if ":" in raw:
        host, _, port = raw.rpartition(":")
        return host or "127.0.0.1", int(port or 1883)
    return raw or "127.0.0.1", 1883


def resolve_mqtt_topics(profile: dict[str, Any], request_id: str) -> tuple[str, str, str]:
    """Return ``(publish_topic, response_topic, mode)`` for a native MQTT round-trip.

    * ``legacy`` mode — endpoint templated as ``<base>/call/{request_id}``; the body
      is the bare ``{uri, payload, context}`` envelope.
    * ``modern`` mode — endpoint is ``<base>/request``; the body carries
      ``request_id`` + ``reply_to`` and the response arrives on ``reply_to``.
    """
    options = _options(profile)
    endpoint = str(profile.get("endpoint") or profile.get("topic") or "").strip()
    response = str(options.get("response_topic") or options.get("reply_to") or "").strip()
    if "{request_id}" in endpoint:
        pub = endpoint.replace("{request_id}", request_id)
        sub_template = response or endpoint.replace("/call/", "/response/")
        sub = sub_template.replace("{request_id}", request_id)
        return pub, sub, "legacy"
    base = endpoint.rsplit("/", 1)[0] if "/" in endpoint else endpoint
    reply_to = (response or f"{base}/response/{request_id}").replace("{request_id}", request_id)
    return endpoint, reply_to, "modern"


def mqtt_native_request(
    *, broker: str, pub_topic: str, sub_topic: str, body: dict[str, Any], timeout: float
) -> dict[str, Any]:
    """Publish *body* to *pub_topic* and wait for one response on *sub_topic*."""
    if MQTT_REQUEST_HOOK is not None:
        return MQTT_REQUEST_HOOK(
            broker=broker, pub_topic=pub_topic, sub_topic=sub_topic, body=body, timeout=timeout
        )
    import paho.mqtt.client as mqtt  # pragma: no cover - requires paho + broker

    host, port = _parse_broker(broker)
    received: dict[str, Any] = {}
    done = threading.Event()

    def on_connect(client, _userdata, _flags, _rc, *_a):
        client.subscribe(sub_topic)

    def on_subscribe(client, _userdata, _mid, _granted, *_a):
        client.publish(pub_topic, json.dumps(body))

    def on_message(_client, _userdata, msg):
        try:
            parsed = json.loads(msg.payload.decode("utf-8"))
            received["data"] = parsed if isinstance(parsed, dict) else {"result": parsed}
        except Exception:
            received["data"] = {}
        done.set()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(host, port, keepalive=max(int(timeout) + 5, 10))
    client.loop_start()
    try:
        if not done.wait(timeout):
            raise TimeoutError(f"mqtt response timeout after {timeout}s on {sub_topic}")
    finally:
        client.loop_stop()
        client.disconnect()
    return received.get("data", {})


def post_json(url: str, body: dict[str, Any], *, timeout: float = 30) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        if not raw.strip():
            return {}
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {"result": parsed}


def _slim_context(context: dict[str, Any]) -> dict[str, Any]:
    skip = {"config", "runtime", "event_store", "state", "params"}
    return {k: v for k, v in context.items() if k not in skip}


def delegate_transport_call(
    *,
    transport: str,
    source_uri: str,
    resolved_uri: str,
    payload: dict[str, Any],
    context: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any] | None:
    """Return a call result when delegated; ``None`` for local in-process execution."""
    transport_key = (transport or "local").lower()
    if transport_key in LOCAL_TRANSPORTS:
        return None

    call_uri = resolved_uri or source_uri
    timeout = float(_options(profile).get("timeout_ms", 30000)) / 1000.0

    if transport_key == "unsupported":
        return {
            "ok": False,
            "uri": source_uri,
            "type": "transport_unsupported",
            "error": profile.get("note") or "transport unsupported on this platform",
        }

    if context.get("dry_run"):
        return {
            "ok": True,
            "uri": source_uri,
            "resolved_uri": resolved_uri,
            "transport": transport_key,
            "delegated": True,
            "result": {"dry_run": True, "would_call": call_uri, "transport": transport_key},
        }

    try:
        if transport_key == "http":
            endpoint = normalize_http_endpoint(profile)
            remote = post_json(
                endpoint,
                {"uri": call_uri, "payload": payload, "context": _slim_context(context)},
                timeout=timeout,
            )
            return _wrap_remote(source_uri, resolved_uri, transport_key, remote)

        if transport_key == "mqtt":
            broker = mqtt_broker_url(profile)
            bridge = mqtt_bridge_url(profile)
            topic = str(profile.get("endpoint") or profile.get("topic") or "").strip()

            # Preferred: native MQTT broker round-trip (no HTTP bridge needed).
            if broker:
                if not mqtt_available():
                    return {
                        "ok": False,
                        "uri": source_uri,
                        "type": "transport_dependency_missing",
                        "error": "native mqtt transport requires paho-mqtt (pip install paho-mqtt) "
                        "or configure options.bridge_url for the HTTP bridge",
                    }
                request_id = uuid.uuid4().hex
                pub_topic, sub_topic, mode = resolve_mqtt_topics(profile, request_id)
                if not pub_topic:
                    return {
                        "ok": False,
                        "uri": source_uri,
                        "type": "transport_config_error",
                        "error": "mqtt transport requires endpoint topic (e.g. <base>/call/{request_id})",
                    }
                envelope = {"uri": call_uri, "payload": payload, "context": _slim_context(context)}
                if mode == "modern":
                    envelope = {"request_id": request_id, "reply_to": sub_topic, **envelope}
                remote = mqtt_native_request(
                    broker=broker, pub_topic=pub_topic, sub_topic=sub_topic, body=envelope, timeout=timeout
                )
                return _wrap_remote(source_uri, resolved_uri, "mqtt", remote)

            # Fallback: forward over an HTTP→MQTT bridge.
            if not bridge:
                return {
                    "ok": False,
                    "uri": source_uri,
                    "type": "transport_config_error",
                    "error": "mqtt transport requires options.broker (native) or "
                    "options.bridge_url / URISYS_MQTT_BRIDGE_URL (http bridge)",
                }
            remote = post_json(
                bridge,
                {
                    "topic": topic,
                    "uri": call_uri,
                    "payload": payload,
                    "context": _slim_context(context),
                    "qos": int(_options(profile).get("qos", 1)),
                },
                timeout=timeout,
            )
            return _wrap_remote(source_uri, resolved_uri, "mqtt", remote)

        if transport_key == "ssh":
            endpoint = str(profile.get("endpoint") or "").strip()
            if endpoint.startswith("http://") or endpoint.startswith("https://"):
                return delegate_transport_call(
                    transport="http",
                    source_uri=source_uri,
                    resolved_uri=resolved_uri,
                    payload=payload,
                    context=context,
                    profile={**profile, "endpoint": endpoint},
                )
            return {
                "ok": False,
                "uri": source_uri,
                "type": "transport_not_implemented",
                "error": f"ssh transport requires http(s) endpoint to remote urisys (got {endpoint!r})",
            }

        return {
            "ok": False,
            "uri": source_uri,
            "type": "transport_unknown",
            "error": f"unknown transport: {transport_key}",
        }
    except Exception as exc:
        return {
            "ok": False,
            "uri": source_uri,
            "resolved_uri": resolved_uri,
            "transport": transport_key,
            "type": "transport_error",
            "error": str(exc),
        }


def _wrap_remote(
    source_uri: str,
    resolved_uri: str,
    transport: str,
    remote: dict[str, Any],
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ok": bool(remote.get("ok", True)),
        "uri": source_uri,
        "resolved_uri": resolved_uri,
        "transport": transport,
        "delegated": True,
        "result": remote.get("result", remote),
    }
    for key in ("error", "type", "operation", "params"):
        if key in remote:
            out[key] = remote[key]
    return out


__all__ = [
    "delegate_transport_call",
    "mqtt_available",
    "mqtt_bridge_url",
    "mqtt_broker_url",
    "mqtt_native_request",
    "normalize_http_endpoint",
    "post_json",
    "resolve_mqtt_topics",
]
