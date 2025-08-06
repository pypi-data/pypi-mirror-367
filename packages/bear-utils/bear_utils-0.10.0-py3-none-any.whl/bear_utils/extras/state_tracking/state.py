"""A class representing a state in a state machine."""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field
from pydantic.dataclasses import dataclass

from bear_utils.extras.state_tracking._common import Auto, get_original


def auto(**kwargs) -> int:
    """A decorator to mark a value as auto-incrementing."""
    auto = Auto()
    return Field(default=auto, **kwargs)


@dataclass
class State:
    """A class representing a state in a state machine."""

    orphaned_states_: ClassVar[list[str]] = []

    state: str = Field(description="The string representation of the state.")
    initial: bool = Field(default=False, description="Whether this state is the initial state of the state machine.")
    final: bool = Field(default=False, description="Whether this state is a final state of the state machine.")
    value: int = auto(description="An integer value representing the state.")

    def __eq__(self, other: object) -> bool:
        """Check equality with another state or integer."""
        if isinstance(other, State):
            return self.value == other.value and self.state == other.state
        if isinstance(other, int):
            return get_original(self.value) == get_original(other)
        if isinstance(other, str):
            return self.state.lower() == other.lower()
        return False

    def __str__(self) -> str:
        """Return the string representation of the state."""
        return self.state.lower()

    def __int__(self) -> int:
        """Return the integer representation of the state value."""
        if isinstance(self.value, (int | Auto)):
            return int(self.value)
        raise TypeError(f"Cannot convert state value '{self.value}' to int.")

    def __hash__(self) -> int:
        """Return the hash of the state value."""
        return hash(get_original(self.value))


__all__ = ["State"]
