"""Extensions to the auto-generated SDK that won't be overwritten during regeneration."""

from .streaming import asyncio_streaming, sync_streaming

__all__ = ["asyncio_streaming", "sync_streaming"]
