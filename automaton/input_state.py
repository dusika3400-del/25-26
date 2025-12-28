"""
Состояние ввода точек.
"""

from typing import Optional
from exceptions import InvalidMenuChoiceException
from input_data import input_by_hand, make_random_points
from automaton.base import AutomatonCoroutine
from automaton.context import AutomatonContext
from automaton.states import State


class InputState(AutomatonCoroutine):
    """Состояние ввода точек."""
    
    def __init__(self, context: AutomatonContext):
        super().__init__(context)
    
    async def run(self) -> Optional[State]:
        print("\n" + "="*40)
        print("ВВОД ТОЧЕК")
        print("="*40)
        print("1. Ручной ввод")
        print("2. Случайная генерация")
        print("0. Назад")
        print("-"*40)
        
        return None
    
    async def handle_input(self, choice: str) -> bool:
        valid_choices = {'0', '1', '2'}
        if choice not in valid_choices:
            raise InvalidMenuChoiceException(choice, valid_choices)
        
        if choice == '0':
            self.next_state = State.MENU
            return True
        
        try:
            if choice == '1':
                await self._input_manual()
            elif choice == '2':
                await self._input_random()
            
            self.next_state = State.PROCESS
            return True
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
    
    async def _input_manual(self):
        """Ручной ввод точек."""
        print("\nРУЧНОЙ ВВОД")
        points = input_by_hand()
        self.context.points = points
    
    async def _input_random(self):
        """Случайная генерация точек."""
        print("\nСЛУЧАЙНАЯ ГЕНЕРАЦИЯ")
        try:
            n = int(input("Сколько точек создать? (5): ") or "5")
            if n <= 0:
                raise ValueError("Количество должно быть положительным")
            
            points = make_random_points(n)
            self.context.points = points
            
        except ValueError as e:
            print(f"Ошибка: {e}")
            raise