"""
Состояние просмотра результатов.
"""

from typing import Optional
from exceptions import InvalidMenuChoiceException
from automaton.base import AutomatonCoroutine
from automaton.context import AutomatonContext
from automaton.states import State


class ViewState(AutomatonCoroutine):
    """Состояние просмотра результатов."""
    
    def __init__(self, context: AutomatonContext):
        super().__init__(context)
    
    async def run(self) -> Optional[State]:
        if not self.context.result:
            print("Нет результатов для отображения!")
            self.next_state = State.PROCESS
            return State.PROCESS
        
        method_names = {
            'original': 'Оригинальный',
            'sequential': 'Последовательный',
            'min_sum': 'Минимальная сумма',
            'min_x': 'Минимальный X'
        }
        
        print("\n" + "="*40)
        print("РЕЗУЛЬТАТЫ ОБРАБОТКИ")
        print("="*40)
        print(f"Метод: {method_names.get(self.context.method, self.context.method)}")
        print(f"Исходные точки: {self.context.points}")
        print(f"Результат: {self.context.result}")
        print("\n" + "-"*40)
        print("1. В главное меню")
        print("2. Выбрать другой метод")
        print("-"*40)
        
        return None
    
    async def handle_input(self, choice: str) -> bool:
        valid_choices = {'1', '2'}
        if choice not in valid_choices:
            raise InvalidMenuChoiceException(choice, valid_choices)
        
        if choice == '1':
            self.next_state = State.MENU
        elif choice == '2':
            self.next_state = State.PROCESS
        
        return True