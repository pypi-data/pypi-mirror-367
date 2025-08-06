from dataclasses import dataclass, field
from typing import Any, Optional
from langchain_core.callbacks import BaseCallbackHandler
from .base import BaseCallContext

class CallContextCallbackHandler(BaseCallbackHandler):
    def __init__(self, ctx: "CallContext"):
        self.ctx = ctx

    def on_llm_start(self, *args, **kwargs):
        self.ctx.set_meta("llm_started", True)

    def on_llm_end(self, response, **kwargs):
        self.ctx.set_meta("llm_ended", True)

    def on_llm_error(self, error: Exception, **kwargs):
        self.ctx.set_error(error)


@dataclass
class CallContext(BaseCallContext):
    user_id: str
    turn_id: str
    meta: dict[str, Any] = field(default_factory=dict)
    """
    A dictionary to store metadata. 
    If the same key is set multiple times, values will be stored in a list.
    """
    error: Optional[Exception] = None
    callbacks: list[CallContextCallbackHandler] = field(default_factory=list)

    def get_user_id(self) -> str:
        return self.user_id

    def get_turn_id(self) -> str:
        return self.turn_id

    def get_meta(self, key: str, all_values: bool = False) -> Any:
        """
        Get meta value(s) for the given key.

        Args:
            key: The meta key to retrieve
            all_values: If True, returns a list of all values for the key.
                      If False (default), returns the most recent value.
        """
        if key not in self.meta:
            return None if not all_values else []

        values = self.meta[key]
        if not isinstance(values, list):
            return values if not all_values else [values]

        return values if all_values else values[-1] if values else None

    def set_meta(self, key: str, value: Any) -> None:
        """
        Set a meta value for the given key.
        If the key already exists, the new value will be appended to a list of values.
        """
        if key in self.meta:
            existing = self.meta[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                self.meta[key] = [existing, value]
        else:
            self.meta[key] = value

    def set_error(self, error: Exception):
        self.error = error

    async def on_complete(self):
        for callback in self.callbacks:
            if callback:
                await callback.call(self)
