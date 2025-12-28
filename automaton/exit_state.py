"""
Состояние выхода.
"""

from typing import Optional
from automaton.base import AutomatonCoroutine
from automaton.context import AutomatonContext
from automaton.states import State


class ExitState(AutomatonCoroutine):
    """Состояние выхода."""
    
    def __init__(self, context: AutomatonContext):
        super().__init__(context)
    
    async def run(self) -> Optional[State]:
        print("\nДо свидания!")
        return State.EXIT
    
    async def handle_input(self, choice: str) -> bool:
        return True