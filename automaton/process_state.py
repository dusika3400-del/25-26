"""
Состояние выбора метода обработки.
"""

from typing import Optional
from exceptions import InvalidMenuChoiceException
from points import process_points
from automaton.base import AutomatonCoroutine
from automaton.context import AutomatonContext
from automaton.states import State


class ProcessState(AutomatonCoroutine):
    """Состояние выбора метода обработки."""
    
    def __init__(self, context: AutomatonContext):
        super().__init__(context)
    
    async def run(self) -> Optional[State]:
        if not self.context.points:
            print("Нет точек для обработки!")
            self.next_state = State.INPUT
            return State.INPUT
        
        print("\n" + "="*40)
        print("ВЫБОР МЕТОДА ОБРАБОТКИ")
        print("="*40)
        
        for key, (_, name) in self.context.methods_map.items():
            print(f"{key}. {name}")
        print("0. Назад")
        print("-"*40)
        
        return None
    
    async def handle_input(self, choice: str) -> bool:
        valid_choices = {'0', '1', '2', '3', '4'}
        if choice not in valid_choices:
            raise InvalidMenuChoiceException(choice, valid_choices)
        
        if choice == '0':
            self.next_state = State.MENU
            return True
        
        method_code, method_name = self.context.methods_map[choice]
        self.context.method = method_code
        
        try:
            print(f"\nОбработка методом '{method_name}'...")
            self.context.result = process_points(self.context.points, method_code)
            self.next_state = State.VIEW
            return True
            
        except Exception as e:
            print(f"Ошибка обработки: {e}")
            return False