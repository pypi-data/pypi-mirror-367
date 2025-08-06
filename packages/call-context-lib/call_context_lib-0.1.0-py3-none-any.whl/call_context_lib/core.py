import inspect
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from inspect import isasyncgen, isgenerator
from typing import Any, Callable, Optional

from .base import BaseCallContext
from .bind import bind


class CallContextCallback(ABC):
    @abstractmethod
    async def call(self, ctx: BaseCallContext) -> None: ...


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
    callbacks: list[CallContextCallback] = field(default_factory=list)

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

    async def on_complete(self):
        for callback in self.callbacks:
            if callback:
                await callback.call(self)

    async def ainvoke(self, fn: Callable, *args, **kwargs):
        try:
            bound = bind(fn, *args, **kwargs)
            result = bound(self)
            if inspect.isawaitable(result):
                result = await result  # ✅ await 가능한 경우
            self.set_meta("output", result)
            return result
        except Exception as e:
            self.error = e
            raise
        finally:
            await self.on_complete()

    async def astream(self, fn: Callable[..., Any], *args, **kwargs) -> AsyncGenerator[str, None]:
        gen = bind(fn, *args, **kwargs)(self)

        if isasyncgen(gen):
            stream = gen
        elif isgenerator(gen):

            async def async_wrapper():
                for item in gen:
                    yield item

            stream = async_wrapper()
        else:
            raise TypeError(f"{fn.__name__} is not a generator or async generator")

        try:
            async for token in stream:
                current = self.get_meta("output") or ""
                self.set_meta("output", current + token)
                yield token
        except Exception as e:
            self.error = e
            raise
        finally:
            await self.on_complete()
