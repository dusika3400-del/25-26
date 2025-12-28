"""
Базовые классы для корутин автомата.
"""

from abc import ABC, abstractmethod
from typing import Optional

from automaton.states import State
from automaton.context import AutomatonContext


class AutomatonCoroutine(ABC):
    """Базовый класс для корутин автомата."""
    
    def __init__(self, context: AutomatonContext):
        self.context = context
        self.next_state: Optional[State] = None
    
    @abstractmethod
    async def run(self) -> Optional[State]:
        """Запуск корутины."""
        pass
    
    @abstractmethod
    async def handle_input(self, input_data: str) -> bool:
        """Обработка ввода пользователя."""
        pass