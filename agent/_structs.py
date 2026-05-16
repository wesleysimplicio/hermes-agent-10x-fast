"""Fast msgspec encoders/decoders for hot-path structures.

Phase 2 (perf): a thin module that exposes precompiled ``msgspec``
encoders/decoders for the canonical types in ``agent.transports.types``.
Reuse the same encoder/decoder instances across the program — msgspec's
JIT setup cost is paid once at import time.

Falls back to ``agent._fastjson`` (orjson/stdlib) when ``msgspec`` is not
installed.
"""

from __future__ import annotations

from typing import Any

from agent.transports.types import ToolCall, Usage  # noqa: F401  (re-export)

try:
    import msgspec as _msgspec  # type: ignore

    _HAVE_MSGSPEC = True
except ImportError:  # pragma: no cover - fallback path
    _HAVE_MSGSPEC = False


if _HAVE_MSGSPEC:
    _tool_call_decoder = _msgspec.json.Decoder(list[ToolCall])
    _single_tool_call_decoder = _msgspec.json.Decoder(ToolCall)
    _encoder = _msgspec.json.Encoder()

    def decode_tool_calls(data: bytes | str) -> list[ToolCall]:
        """Decode a JSON array of tool calls into ``list[ToolCall]``."""
        if isinstance(data, str):
            data = data.encode()
        return _tool_call_decoder.decode(data)

    def decode_tool_call(data: bytes | str) -> ToolCall:
        if isinstance(data, str):
            data = data.encode()
        return _single_tool_call_decoder.decode(data)

    def encode(obj: Any) -> bytes:
        """Fast encode any msgspec.Struct or compatible value to JSON bytes."""
        return _encoder.encode(obj)

    def encode_str(obj: Any) -> str:
        return _encoder.encode(obj).decode("utf-8")

else:
    from agent import _fastjson as _fj

    def decode_tool_calls(data: bytes | str) -> list[ToolCall]:
        items = _fj.loads(data)
        result: list[ToolCall] = []
        for it in items or []:
            fn = it.get("function") or {}
            result.append(
                ToolCall(
                    id=it.get("id"),
                    name=fn.get("name") or it.get("name") or "",
                    arguments=fn.get("arguments") or it.get("arguments") or "",
                    provider_data=None,
                )
            )
        return result

    def decode_tool_call(data: bytes | str) -> ToolCall:
        it = _fj.loads(data)
        fn = it.get("function") or {}
        return ToolCall(
            id=it.get("id"),
            name=fn.get("name") or it.get("name") or "",
            arguments=fn.get("arguments") or it.get("arguments") or "",
            provider_data=None,
        )

    def encode(obj: Any) -> bytes:
        return _fj.dumps(obj).encode("utf-8")

    def encode_str(obj: Any) -> str:
        return _fj.dumps(obj)


__all__ = [
    "ToolCall",
    "Usage",
    "decode_tool_calls",
    "decode_tool_call",
    "encode",
    "encode_str",
]
