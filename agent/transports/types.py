"""Shared types for normalized provider responses.

These structs define the canonical shape that all provider adapters
normalize responses to.  The shared surface is intentionally minimal —
only fields that every downstream consumer reads are top-level.
Protocol-specific state goes in ``provider_data`` dicts (response-level
and per-tool-call) so that protocol-aware code paths can access it
without polluting the shared type.

Phase 2 (perf): backing storage migrated from ``@dataclass`` to
``msgspec.Struct`` (``gc=False``) for zero-allocation decode and ~3-5x
faster attribute access on the hot tool-call path. Falls back to
``@dataclass`` when ``msgspec`` is not installed (Termux, source-only).
"""

from __future__ import annotations

import json
from typing import Any

try:
    import msgspec as _msgspec  # type: ignore

    _HAVE_MSGSPEC = True
except ImportError:  # pragma: no cover - fallback path
    _HAVE_MSGSPEC = False


if _HAVE_MSGSPEC:

    class ToolCall(_msgspec.Struct, gc=False, kw_only=False):
        """A normalized tool call from any provider.

        ``id`` is the protocol's canonical identifier — what gets used in
        ``tool_call_id`` / ``tool_use_id`` when constructing tool result
        messages.  May be ``None`` when the provider omits it; the agent
        fills it via ``_deterministic_call_id()`` before storing in history.

        ``provider_data`` carries per-tool-call protocol metadata that only
        protocol-aware code reads:

        * Codex: ``{"call_id": "call_XXX", "response_item_id": "fc_XXX"}``
        * Gemini: ``{"extra_content": {"google": {"thought_signature": "..."}}}``
        * Others: ``None``
        """

        id: str | None
        name: str
        arguments: str
        provider_data: dict[str, Any] | None = None

        @property
        def type(self) -> str:
            return "function"

        @property
        def function(self) -> "ToolCall":
            """Return self so ``tc.function.name`` / ``tc.function.arguments`` work."""
            return self

        @property
        def call_id(self) -> str | None:
            return (self.provider_data or {}).get("call_id")

        @property
        def response_item_id(self) -> str | None:
            return (self.provider_data or {}).get("response_item_id")

        @property
        def extra_content(self) -> dict[str, Any] | None:
            return (self.provider_data or {}).get("extra_content")

    class Usage(_msgspec.Struct, gc=False, kw_only=False):
        """Token usage from an API response."""

        prompt_tokens: int = 0
        completion_tokens: int = 0
        total_tokens: int = 0
        cached_tokens: int = 0

    class NormalizedResponse(_msgspec.Struct, gc=False, kw_only=False):
        """Normalized API response from any provider."""

        content: str | None
        tool_calls: list[ToolCall] | None
        finish_reason: str
        reasoning: str | None = None
        usage: Usage | None = None
        provider_data: dict[str, Any] | None = None

        @property
        def reasoning_content(self) -> str | None:
            pd = self.provider_data or {}
            return pd.get("reasoning_content")

        @property
        def reasoning_details(self):
            pd = self.provider_data or {}
            return pd.get("reasoning_details")

        @property
        def codex_reasoning_items(self):
            pd = self.provider_data or {}
            return pd.get("codex_reasoning_items")

        @property
        def codex_message_items(self):
            pd = self.provider_data or {}
            return pd.get("codex_message_items")

else:
    from dataclasses import dataclass, field

    @dataclass
    class ToolCall:  # type: ignore[no-redef]
        id: str | None
        name: str
        arguments: str
        provider_data: dict[str, Any] | None = field(default=None, repr=False)

        @property
        def type(self) -> str:
            return "function"

        @property
        def function(self) -> "ToolCall":
            return self

        @property
        def call_id(self) -> str | None:
            return (self.provider_data or {}).get("call_id")

        @property
        def response_item_id(self) -> str | None:
            return (self.provider_data or {}).get("response_item_id")

        @property
        def extra_content(self) -> dict[str, Any] | None:
            return (self.provider_data or {}).get("extra_content")

    @dataclass
    class Usage:  # type: ignore[no-redef]
        prompt_tokens: int = 0
        completion_tokens: int = 0
        total_tokens: int = 0
        cached_tokens: int = 0

    @dataclass
    class NormalizedResponse:  # type: ignore[no-redef]
        content: str | None
        tool_calls: list[ToolCall] | None
        finish_reason: str
        reasoning: str | None = None
        usage: Usage | None = None
        provider_data: dict[str, Any] | None = field(default=None, repr=False)

        @property
        def reasoning_content(self) -> str | None:
            pd = self.provider_data or {}
            return pd.get("reasoning_content")

        @property
        def reasoning_details(self):
            pd = self.provider_data or {}
            return pd.get("reasoning_details")

        @property
        def codex_reasoning_items(self):
            pd = self.provider_data or {}
            return pd.get("codex_reasoning_items")

        @property
        def codex_message_items(self):
            pd = self.provider_data or {}
            return pd.get("codex_message_items")


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def build_tool_call(
    id: str | None,
    name: str,
    arguments: Any,
    **provider_fields: Any,
) -> ToolCall:
    """Build a ``ToolCall``, auto-serialising *arguments* if it's a dict.

    Any extra keyword arguments are collected into ``provider_data``.
    """
    args_str = json.dumps(arguments) if isinstance(arguments, dict) else str(arguments)
    pd = dict(provider_fields) if provider_fields else None
    return ToolCall(id=id, name=name, arguments=args_str, provider_data=pd)


def map_finish_reason(reason: str | None, mapping: dict[str, str]) -> str:
    """Translate a provider-specific stop reason to the normalised set.

    Falls back to ``"stop"`` for unknown or ``None`` reasons.
    """
    if reason is None:
        return "stop"
    return mapping.get(reason, "stop")
