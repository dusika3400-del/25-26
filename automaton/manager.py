"""
Менеджер конечного автомата.
"""

import asyncio
from exceptions import InvalidMenuChoiceException

from automaton.states import State
from automaton.context import AutomatonContext
from automaton.menu_state import MenuState
from automaton.input_state import InputState
from automaton.process_state import ProcessState
from automaton.view_state import ViewState
from automaton.exit_state import ExitState


class AutomatonManager:
    """Менеджер конечного автомата."""
    
    def __init__(self):
        self.state = State.MENU
        self.context = AutomatonContext()
        self.coroutines = {
            State.MENU: MenuState(self.context),
            State.INPUT: InputState(self.context),
            State.PROCESS: ProcessState(self.context),
            State.VIEW: ViewState(self.context),
            State.EXIT: ExitState(self.context)
        }
    
    def run(self):
        """Основной цикл автомата."""
        asyncio.run(self._run_async())
    
    async def _run_async(self):
        """Асинхронный основной цикл автомата."""
        print("\n" + "="*50)
        print("АВТОМАТНОЕ ПРОГРАММИРОВАНИЕ")
        print("ОБРАБОТКА ТОЧЕК НА ПЛОСКОСТИ")
        print("="*50)
        
        while self.state != State.EXIT:
            try:
                # Получаем текущую корутину
                coroutine = self.coroutines[self.state]
                
                # Запускаем корутину
                next_state = await coroutine.run()
                
                # Если корутина вернула следующее состояние, переходим
                if next_state:
                    self.state = next_state
                    continue
                
                # Получаем ввод пользователя
                if self.state == State.MENU:
                    prompt = "Ваш выбор (1-3): "
                else:
                    prompt = "Ваш выбор: "
                
                user_input = input(prompt).strip()
                
                # Обрабатываем ввод через корутину
                success = await coroutine.handle_input(user_input)
                
                if success and coroutine.next_state:
                    self.state = coroutine.next_state
                
            except InvalidMenuChoiceException as e:
                print(f"{e}")
            except KeyboardInterrupt:
                print("\n\nПрограмма прервана")
                self.state = State.EXIT
            except Exception as e:
                print(f"Критическая ошибка: {e}")
                self.state = State.MENU