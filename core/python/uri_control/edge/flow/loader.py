from __future__ import annotations

from pathlib import Path
from typing import Any


def load_yaml_flow(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except Exception:
        # tiny fallback for simple examples
        data: dict[str, Any] = {"do": [], "defaults": {}}
        current = None
        active_item: dict[str, Any] | None = None
        for raw in text.splitlines():
            line = raw.rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped in ("defaults:", "do:"):
                current = stripped[:-1]
                continue
            if current == "do" and stripped.startswith("- "):
                item = stripped[2:]
                if item.endswith(":"):
                    active_item = {item[:-1]: {}}
                    data["do"].append(active_item)
                else:
                    active_item = None
                    data["do"].append(item)
            elif current == "do" and active_item and ":" in stripped:
                key, value = stripped.split(":", 1)
                uri = next(iter(active_item.keys()))
                value = value.strip()
                if value.isdigit():
                    parsed: Any = int(value)
                elif value.lower() in ("true", "false"):
                    parsed = value.lower() == "true"
                else:
                    parsed = value
                active_item[uri][key.strip()] = parsed
        return data

