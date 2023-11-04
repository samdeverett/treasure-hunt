"""An agent's potential actions."""

from enum import IntEnum


class Actions(IntEnum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3
    Stay = 4
