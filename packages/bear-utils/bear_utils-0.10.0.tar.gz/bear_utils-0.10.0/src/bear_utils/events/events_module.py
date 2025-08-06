"""Event handling module for Bear Utils."""

from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from types import MethodType
from typing import Any, Literal, overload
import weakref
from weakref import WeakMethod

from bear_utils.extras._async_helpers import AsyncResponseModel, create_async_task, is_async_function

Callback = Callable[..., Any]

_event_registry: dict[str, weakref.WeakSet[Callback]] = defaultdict(weakref.WeakSet)


def clear_handlers_for_event(event_name: str) -> None:
    """Remove all handlers associated with a specific event."""
    _event_registry.pop(event_name, None)


def clear_all() -> None:
    """Remove all registered event handlers."""
    _event_registry.clear()


def _make_callback(name: str) -> Callable[[Any], None]:
    """Create an internal callback to remove dead handlers."""

    def callback(weak_method: Any) -> None:
        _event_registry[name].remove(weak_method)
        if not _event_registry[name]:
            del _event_registry[name]

    return callback


def set_handler(name: str, func: Callback) -> None:
    """Register a function as a handler for a specific event."""
    if isinstance(func, MethodType):
        _event_registry[name].add(WeakMethod(func, _make_callback(name)))
    else:
        _event_registry[name].add(func)


@overload
def dispatch_event(name: str, single: Literal[True], *args, **kwargs) -> Any: ...


@overload
def dispatch_event(name: str, single: Literal[False] = False, *args, **kwargs) -> list[Any]: ...


def dispatch_event(name: str, single: bool = False, *args, **kwargs) -> list[Any]:
    """Dispatch an event to all registered handlers."""
    results: list[Any] = []
    for func in _event_registry.get(name, []):
        if is_async_function(func):
            task: AsyncResponseModel = create_async_task(func(*args, **kwargs))
            result = task.get_conditional_result(timeout=1)
            results.append(result)
        else:
            result: Any = func(*args, **kwargs)
            results.append(result)
    if single and len(results) == 1:
        return results[0]
    return results


def event_handler(event_name: str) -> Callable[[Callback], Callback]:
    """Decorator to register a callback as an event handler for a specific event."""

    def decorator(callback: Callback) -> Callback:
        @wraps(callback)
        def wrapper(*args, **kwargs) -> Any:
            """Wrapper to register the callback and call it."""
            return callback(*args, **kwargs)

        set_handler(event_name, wrapper)
        return wrapper

    return decorator
