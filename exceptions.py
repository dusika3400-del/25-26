"""
Кастомные исключения для проекта обработки точек.

Реализует иерархию исключений по принципам из PDF-файлов:
1. Базовый класс для категоризации
2. Конкретные исключения с полезной информацией
3. Принцип Tell-Don't-Ask
"""


class PointsProcessorException(Exception):
    """Базовое исключение для всех ошибок в проекте обработки точек."""
    pass


class InputException(PointsProcessorException):
    """Исключения, связанные с вводом данных."""
    pass


class InvalidInputFormatException(InputException):
    """Некорректный формат ввода."""
    
    def __init__(self, user_input):
        self.user_input = user_input
        super().__init__(f"Некорректный формат ввода: '{user_input}'. Ожидается формат 'x,y'")


class InvalidNumberException(InputException):
    """Некорректное числовое значение."""
    
    def __init__(self, value, field="число"):
        self.value = value
        self.field = field
        super().__init__(f"Некорректное значение {field}: '{value}'. Ожидается число")


class ProcessingException(PointsProcessorException):
    """Исключения, связанные с обработкой точек."""
    pass


class EmptyPointsListException(ProcessingException):
    """Пустой список точек."""
    
    def __init__(self):
        super().__init__("Список точек пуст. Нечего обрабатывать")


class InsufficientPointsException(ProcessingException):
    """Недостаточно точек для операции."""
    
    def __init__(self, required=2, actual=1):
        self.required = required
        self.actual = actual
        super().__init__(f"Недостаточно точек: требуется {required}, доступно {actual}")


class InvalidMethodException(ProcessingException):
    """Некорректный метод обработки."""
    
    def __init__(self, method):
        self.method = method
        super().__init__(f"Неизвестный метод обработки: '{method}'")


class CalculationException(PointsProcessorException):
    """Исключения, связанные с вычислениями."""
    pass


class DistanceCalculationException(CalculationException):
    """Ошибка при вычислении расстояния."""
    
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        super().__init__(f"Ошибка при вычислении расстояния между точками {p1} и {p2}")


class MenuException(PointsProcessorException):
    """Исключения, связанные с меню."""
    pass


class InvalidMenuChoiceException(MenuException):
    """Некорректный выбор в меню."""
    
    def __init__(self, choice, valid_choices=None):
        self.choice = choice
        self.valid_choices = valid_choices
        
        if valid_choices:
            message = f"Некорректный выбор: '{choice}'. Допустимые значения: {valid_choices}"
        else:
            message = f"Некорректный выбор: '{choice}'"
        
        super().__init__(message)


class LoggingException(PointsProcessorException):
    """Исключения, связанные с логированием."""
    pass


class InvalidLoggingLevelException(LoggingException):
    """Некорректный уровень логирования."""
    
    def __init__(self, level):
        self.level = level
        super().__init__(f"Некорректный уровень логирования: '{level}'")