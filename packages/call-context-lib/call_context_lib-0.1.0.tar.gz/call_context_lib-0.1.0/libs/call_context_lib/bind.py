import inspect
from typing import Any, Callable


# Placeholder object for context injection
class _ContextPlaceholder:
    """Placeholder object used to indicate where context should be injected"""

    pass


_ = _ContextPlaceholder()

# 각각의 fn 특성에 따라 명시적으로 분리된 bind 함수


def bind_asyncgen(fn, *args, **kwargs):
    def wrapped(ctx):
        bound_args = [ctx if isinstance(arg, _ContextPlaceholder) else arg for arg in args]
        bound_kwargs = {
            k: (ctx if isinstance(v, _ContextPlaceholder) else v) for k, v in kwargs.items()
        }
        return fn(*bound_args, **bound_kwargs)  # AsyncGenerator expected

    return wrapped


def bind_awaitable(fn, *args, **kwargs):
    def wrapped(ctx):
        bound_args = [ctx if isinstance(arg, _ContextPlaceholder) else arg for arg in args]
        bound_kwargs = {
            k: (ctx if isinstance(v, _ContextPlaceholder) else v) for k, v in kwargs.items()
        }
        return fn(*bound_args, **bound_kwargs)  # Coroutine expected

    return wrapped


def bind_sync(fn, *args, **kwargs):
    def wrapped(ctx):
        bound_args = [ctx if isinstance(arg, _ContextPlaceholder) else arg for arg in args]
        bound_kwargs = {
            k: (ctx if isinstance(v, _ContextPlaceholder) else v) for k, v in kwargs.items()
        }
        return fn(*bound_args, **bound_kwargs)  # Sync function

    return wrapped


# 자동 추론 bind: 반환 타입을 기반으로 bind 전략을 자동 선택


def autobind(fn: Callable[..., Any], *args, **kwargs) -> Callable[[Any], Any]:
    def dispatcher(ctx):
        bound_args = [ctx if isinstance(arg, _ContextPlaceholder) else arg for arg in args]
        bound_kwargs = {
            k: (ctx if isinstance(v, _ContextPlaceholder) else v) for k, v in kwargs.items()
        }

        # fn 자체가 Callable[[ctx]], 즉 이미 bind된 형태로 들어온 경우
        if not callable(fn):
            raise TypeError("Provided fn is not callable")

        actual_fn = fn
        if callable(fn) and hasattr(fn, "__wrapped__"):
            actual_fn = fn.__wrapped__  # unwrap if needed

        result = actual_fn(*bound_args, **bound_kwargs)
        if inspect.isawaitable(result):

            async def async_wrapper():
                return await result

            return async_wrapper()
        return result

    return dispatcher


# fallback bind: alias for autobind
bind = autobind
