"""A class representing a state in a state machine."""

from __future__ import annotations

from pydantic import Field
from pydantic.dataclasses import dataclass

from bear_utils.extras.state_tracking._common import Auto, get_original


def auto(**kwargs) -> int:
    """A decorator to mark a value as auto-incrementing."""
    auto = Auto(0)
    return Field(default=auto, **kwargs)


@dataclass
class State:
    """A class representing a state in a state machine."""

    name: str = Field(description="The string representation of the state.")
    initial: bool = Field(default=False, description="Whether this state is the initial state of the state machine.")
    final: bool = Field(default=False, description="Whether this state is a final state of the state machine.")
    id: int = auto(description="An integer value representing the state.")

    def __eq__(self, other: object) -> bool:
        """Check equality with another state or integer."""
        if isinstance(other, State):
            return self.id == other.id and self.name == other.name
        if isinstance(other, int):
            return get_original(self.id) == get_original(other)
        if isinstance(other, str):
            return self.name.upper() == other.upper()
        return False

    def __str__(self) -> str:
        """Return the string representation of the state."""
        return self.name.upper()

    def __int__(self) -> int:
        """Return the integer representation of the state value."""
        if isinstance(self.id, (int | Auto)):
            return int(self.id)
        raise TypeError(f"Cannot convert state value '{self.id}' to int.")

    def __hash__(self) -> int:
        """Return the hash of the state value."""
        return hash(get_original(self.id))


__all__ = ["State"]
