"""
Состояние главного меню.
"""

from typing import Optional
from exceptions import InvalidMenuChoiceException
from automaton.base import AutomatonCoroutine
from automaton.context import AutomatonContext
from automaton.states import State
from points import process_points


class MenuState(AutomatonCoroutine):
    """Главное меню."""
    
    def __init__(self, context: AutomatonContext):
        super().__init__(context)
    
    async def run(self) -> Optional[State]:
        print("\n" + "="*40)
        print("ГЛАВНОЕ МЕНЮ")
        print("="*40)
        print("1. Обработать точки")
        print("2. Сравнить все методы")
        print("3. Выход")
        print("-"*40)
        
        return None
    
    async def handle_input(self, choice: str) -> bool:
        valid_choices = {'1', '2', '3'}
        if choice not in valid_choices:
            raise InvalidMenuChoiceException(choice, valid_choices)
        
        if choice == '1':
            self.next_state = State.INPUT
        elif choice == '2':
            self.next_state = State.MENU
            await self._compare_methods()
        elif choice == '3':
            self.next_state = State.EXIT
        
        return True
    
    async def _compare_methods(self):
        """Сравнение всех методов обработки."""
        if not self.context.points:
            print("\nНет точек для сравнения!")
            print("Сначала введите точки (выберите пункт 1)")
            return
        
        print("\n" + "="*40)
        print("СРАВНЕНИЕ ВСЕХ МЕТОДОВ")
        print("="*40)
        
        for method_key, (method_code, method_name) in self.context.methods_map.items():
            try:
                result = process_points(self.context.points, method_code)
                print(f"{method_name}:")
                print(f"   Результат: {result}")
            except Exception as e:
                print(f"{method_name}: ошибка - {e}")
        
        print("\nНажмите Enter для продолжения...")
        input()