from __future__ import annotations

from inspect import isclass
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from collections.abc import Callable


class StateTransitionError(Exception):
    """Custom exception for state transition errors."""


def determine_calling_class(stack_offset: int) -> str:
    """Determine the calling class name from the stack frame."""
    import inspect  # noqa: PLC0415
    from inspect import FrameInfo  # noqa: PLC0415

    frames: list[FrameInfo] = inspect.stack()[stack_offset:]
    for frame in frames:
        if frame.frame.f_locals.get("__qualname__") is not None:
            return frame.frame.f_locals["__qualname__"]
        if frame.function != "<module>":
            return frame.function
    raise RuntimeError("Could not determine calling class name.")


class AutoValue:
    _counters: ClassVar[dict[str, int]] = {}
    _last_set_values: ClassVar[dict[str, int | None]] = {}
    _stack_offset: ClassVar[int] = 4
    _stored_class_name: ClassVar[str | None] = None

    @classmethod
    def set_class_name(cls, class_name: str) -> None:
        """Set the class name for the AutoValue counter.

        Args:
            class_name (str): The class name to set.
        """
        cls._stored_class_name = class_name
        if class_name not in cls._counters:
            cls._counters[class_name] = 0
            cls._last_set_values[class_name] = None

    def __new__(cls) -> int:
        if cls._stored_class_name is not None:
            class_name = cls._stored_class_name
            print(f"AutoValue called from stored class: {class_name}")
        else:
            class_name: str = determine_calling_class(stack_offset=cls._stack_offset)
            print(f"AutoValue called from class: {class_name}")
        if class_name not in cls._counters:
            cls._counters[class_name] = 0
            cls._last_set_values[class_name] = None

        result: int = cls._counters[class_name]
        cls._counters[class_name] += 1
        return result

    @classmethod
    def set_from(cls, value: int) -> None:
        if cls._stored_class_name is not None:
            class_name = cls._stored_class_name
        else:
            class_name: str = determine_calling_class(stack_offset=cls._stack_offset)
        print(f"Setting _AutoValue for class: {class_name} to {value}")
        if class_name not in cls._counters:
            cls._counters[class_name] = 0
            cls._last_set_values[class_name] = None

        cls._counters[class_name] = value + 1
        cls._last_set_values[class_name] = value


def auto_value(extra_offset: int = 1) -> int:
    """Function to return an auto-incremented value.

    Args:
        extra_offset (int): The number of stack frames to skip to find the calling context.

    Returns:
        AutoValue: An instance of AutoValue that provides an auto-incremented value.
    """
    new_class = type("AutoValue_func", (AutoValue,), {})
    new_class._stack_offset += extra_offset  # Adjust stack offset for the
    return new_class()


@dataclass
class State:
    """A class representing a state in a state machine."""

    state: str = Field(description="The textual representation of the state.")
    initial: bool = Field(default=False, description="Whether this state is the initial state of the state machine.")
    final: bool = Field(default=False, description="Whether this state is a final state of the state machine.")
    value: int = Field(
        default_factory=lambda: auto_value(),
        description="Auto-incremented value for the state.",
        json_schema_extra={"auto": True},
    )

    @field_validator("value", mode="before")
    @classmethod
    def handle_manual_values(cls, v: int) -> int:
        if isinstance(v, int):
            AutoValue.set_from(v)
        return v

    def __eq__(self, other: object) -> bool:
        """Check equality with another state or integer."""
        if isinstance(other, State):
            return self.value == other.value and self.state == other.state
        if isinstance(other, int):
            return self.value == other
        return False

    def __str__(self) -> str:
        """Return the string representation of the state."""
        return self.state.lower()

    def __int__(self) -> int:
        """Return the integer representation of the state value."""
        if isinstance(self.value, int):
            return self.value
        raise TypeError(f"Cannot convert state value '{self.value}' to int.")

    def __hash__(self) -> int:
        """Return the hash of the state value."""
        return hash(self.value)


class StateMachine:
    """A base class for state machines, providing a mapping of states and an initial state."""

    def __init__(self) -> None:
        """Initialize the StateMachine."""
        self.state_map: dict[str, State] = {
            attr: value for attr, value in self.__class__.__dict__.items() if isinstance(value, State)
        }
        self._initial_state: State | None = next((state for state in self.state_map.values() if state.initial), None)
        self._current_state: State = self._initial_state if self._initial_state else next(iter(self.state_map.values()))

    def has(self, state: State | Any) -> bool:
        """Check if the state machine has a specific state."""
        state = self._get(state)
        if state is None:
            return False
        return bool(isinstance(state, State))

    def _get_by_name(self, name: str) -> State:
        """Get a state by its name."""
        name_get: State | None = self.state_map.get(name)
        if name_get is None:
            raise ValueError(f"State '{name_get}' not found in the state machine.")
        return name_get

    def _get_by_value(self, value: int) -> State:
        """Get a state by its integer value."""
        value_get: State | None = next((s for s in self.state_map.values() if s.value == value), None)
        if value_get is None:
            raise ValueError(f"State with value '{value}' not found in the state machine.")
        return value_get

    def _get(self, state: State | str | int, default: Any = None) -> State:
        """Get a state by its name or value."""
        try:
            if isinstance(state, State):
                return state
            if isinstance(state, str):
                return self._get_by_name(state)
            if isinstance(state, int):
                return self._get_by_value(state)
        except (ValueError, TypeError):
            return default

    @property
    def current_state(self) -> State:
        """Get the current state of the state machine."""
        return self._current_state

    @current_state.setter
    def current_state(self, state: State | str | int | Any) -> None:
        """Set the current state of the state machine.

        Args:
            state (State | str | int): The new state to set. Can be a State instance, a string name, or an integer value.

        Raises:
            ValueError: If the state is not defined in the state machine.
            TypeError: If the provided state is not a valid type (State, str, or int).
            StateTransitionError: If the state is final or initial and cannot be set as the current state.
        """
        if self.current_state.final:
            raise StateTransitionError(f"Cannot change from final state {self.current_state}.")

        if not self.has(state):
            raise ValueError(f"State {state} is not defined in the state machine.")
        if not isinstance(state, (State | str | int)):
            raise TypeError(f"Invalid state: {state}")

        state = self._get(state)

        if state.state == self.current_state.state:
            return

        if state.initial:
            raise StateTransitionError(f"Cannot set initial state {state} as current state.")

        self._current_state = state

    def set_state(self, state: State | int | str) -> None:
        """Set the current state of the state machine."""
        self.current_state = state


def if_auto(state: State) -> bool:
    try:
        json_extra: dict = state.__dataclass_fields__["value"].default.json_schema_extra
        return json_extra.get("auto", False)
    except Exception:
        return False


def auto_value_decorator() -> Callable[[type], Any]:
    """Decorator to find capitalized strings in a class and convert them to State instances with auto-incremented values."""

    def decorator(cls: type) -> Any:
        """Decorator function to convert class attributes to State instances with auto-incremented values."""
        if not isclass(cls):
            raise TypeError("auto_value_decorator can only be applied to classes.")
        cls_name: str = cls.__name__
        new_type = type(f"AutoValue_{cls_name}", (AutoValue,), {})
        new_type.set_class_name(cls_name)
        for name in dir(cls):
            if not name.startswith("_") and name.isupper():
                attr: str | State | Any = getattr(cls, name)
                if not isinstance(attr, State) and isinstance(attr, str):
                    setattr(cls, name, State(state=name, value=new_type()))
        return cls

    return decorator


__all__ = ["AutoValue", "State", "StateMachine", "StateTransitionError"]

# if __name__ == "__main__":
#     # Example usage
#     from rich import inspect

#     @auto_value_decorator()
#     class MyStateMachine(StateMachine):
#         START = State("start", initial=True)
#         PROCESSING = State("processing")
#         DONE = State("done", final=True)

#     @auto_value_decorator()
#     class MyStateMachineWithManualValues(StateMachine):
#         IDLE = State("idle")
#         RUNNING = State("running")
#         WARNING = State("warning", value=10)  # Manual value = 10
#         CRITICAL = State("critical")  # value = 11 (continues from manual

#     sm = MyStateMachine()
#     inspect(sm)

#     sm_with_manual = MyStateMachineWithManualValues()
#     inspect(sm_with_manual)
