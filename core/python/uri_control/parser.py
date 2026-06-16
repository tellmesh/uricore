from __future__ import annotations

from urllib.parse import parse_qsl, urlsplit

from .errors import UriParseError
from .models import ParsedUri


def parse_uri(uri: str) -> ParsedUri:
    """Parse a URI into a stable internal structure.

    The parser intentionally keeps the model simple. For custom schemes, it treats
    the URI body after ``scheme://`` as ``authority/path``.
    """

    if not isinstance(uri, str) or not uri.strip():
        raise UriParseError("URI must be a non-empty string.")

    raw = uri.strip()
    parts = urlsplit(raw)

    if not parts.scheme:
        raise UriParseError(f"URI has no scheme: {uri!r}")

    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    path = tuple(segment for segment in parts.path.split("/") if segment)

    return ParsedUri(
        raw=raw,
        scheme=parts.scheme,
        authority=parts.netloc,
        path=path,
        query=query,
        fragment=parts.fragment or None,
    )


def canonicalize_uri(uri: str) -> str:
    """Return a conservative canonical string.

    This does not reorder query parameters because some protocols may treat
    ordering as meaningful. It only trims whitespace and validates the URI.
    """

    return parse_uri(uri).raw
