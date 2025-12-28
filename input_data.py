import random
from exceptions import InvalidInputFormatException, InvalidNumberException


def input_by_hand():
    """
    Интерактивный ввод точек с клавиатуры.
    
    Returns
    -------
    list
        Список точек
    
    Raises
    ------
    InvalidInputFormatException
        Если формат ввода некорректен
    InvalidNumberException
        Если введено некорректное число
    """
    points = []
    print("\n=== Ручной ввод ===")
    print("Формат: x,y  (например: 3,4)")
    print("Для выхода введите 'стоп'")
    
    count = 1
    while True:
        try:
            user = input(f"Точка {count}: ").strip()
            
            if user.lower() in ['стоп', 'stop', '']:
                break
            
            parts = user.split(',')
            if len(parts) != 2:
                raise InvalidInputFormatException(user)
            
            try:
                x = float(parts[0])
            except ValueError:
                raise InvalidNumberException(parts[0], "координата X")
            
            try:
                y = float(parts[1])
            except ValueError:
                raise InvalidNumberException(parts[1], "координата Y")
            
            points.append((x, y))
            count += 1
        
        except (InvalidInputFormatException, InvalidNumberException) as e:
            print(f"Ошибка: {e}")
            continue
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            continue
    
    print(f"Введено точек: {len(points)}")
    return points


def make_random_points(n=5):
    """
    Генерация случайных точек для тестирования.
    
    Parameters
    ----------
    n : int
        Количество точек
    
    Returns
    -------
    list
        Список точек
    
    Raises
    ------
    InvalidNumberException
        Если количество точек некорректно
    """
    if n <= 0:
        raise InvalidNumberException(n, "количество точек")
    
    points = []
    for i in range(n):
        x = random.randint(-10, 10)
        y = random.randint(-10, 10)
        points.append((x, y))
    
    print(f"Создано {n} случайных точек")
    return points