"""Drop-in fast JSON wrapper.

orjson is 2-10x faster than stdlib json for both encode and decode, and is
the canonical choice for hot paths (per-message and per-token). This module
exposes a tiny surface mimicking the subset of stdlib json that the
hermes-agent hot paths actually use, with graceful fallback to stdlib json
when orjson is unavailable (Termux, source-only installs, locked-down
envs).

Usage:

    from agent._fastjson import loads, dumps

Semantics:

- ``loads(s)`` accepts str OR bytes; returns native Python objects.
- ``dumps(obj, *, ensure_ascii=False, sort_keys=False, indent=None)`` returns
  a ``str``. orjson native return is bytes; we ``.decode()`` to keep API
  parity with stdlib for callers that splice into f-strings, log lines or
  HTTP bodies.

Only the kwargs we actually use across the hot paths are supported. Anything
beyond that should fall through to stdlib by importing ``json`` directly.
"""

from __future__ import annotations

from typing import Any

try:
    import orjson as _orjson  # type: ignore

    _HAVE_ORJSON = True
except ImportError:  # pragma: no cover — fallback path
    import json as _json  # type: ignore

    _HAVE_ORJSON = False


def loads(s: Any) -> Any:
    if _HAVE_ORJSON:
        return _orjson.loads(s)
    return _json.loads(s)


def dumps(
    obj: Any,
    *,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    indent: int | None = None,
    default: Any = None,
) -> str:
    if _HAVE_ORJSON:
        opt = 0
        if sort_keys:
            opt |= _orjson.OPT_SORT_KEYS
        if indent == 2:
            opt |= _orjson.OPT_INDENT_2
        elif indent is not None and indent != 0:
            import json as _json_local
            return _json_local.dumps(
                obj,
                ensure_ascii=ensure_ascii,
                sort_keys=sort_keys,
                indent=indent,
                default=default,
            )
        if default is not None:
            return _orjson.dumps(obj, default=default, option=opt).decode("utf-8")
        return _orjson.dumps(obj, option=opt).decode("utf-8")
    if default is not None:
        return _json.dumps(
            obj,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            indent=indent,
            default=default,
        )
    return _json.dumps(
        obj, ensure_ascii=ensure_ascii, sort_keys=sort_keys, indent=indent
    )


__all__ = ["loads", "dumps"]
