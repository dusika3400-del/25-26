"""
Контекст для хранения данных между состояниями.
"""


class AutomatonContext:
    """Контекст для хранения данных между состояниями."""
    
    def __init__(self):
        self.points = []
        self.method = None
        self.result = None
        self.methods_map = {
            '1': ('original', 'Оригинальный (ближайшая)'),
            '2': ('sequential', 'Последовательный'),
            '3': ('min_sum', 'Минимальная сумма'),
            '4': ('min_x', 'Минимальный X')
        }