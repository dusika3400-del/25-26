"""
Состояния конечного автомата.
"""

from enum import Enum


class State(Enum):
    """Состояния конечного автомата."""
    MENU = "menu"
    INPUT = "input"
    PROCESS = "process"
    VIEW = "view"
    EXIT = "exit"