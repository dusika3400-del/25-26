from distance import find_closest
from exceptions import (
    InvalidMethodException, 
    EmptyPointsListException,
    InsufficientPointsException
)


def add_two_points(p1, p2):
    """
    Складывает координаты двух точек.
    
    Raises
    ------
    ValueError
        Если точки некорректны
    """
    try:
        return (p1[0] + p2[0], p1[1] + p2[1])
    except (TypeError, IndexError) as e:
        raise ValueError(f"Некорректные точки: {p1}, {p2}") from e


def process_points(points, method="original"):
    """
    Универсальная функция для выбора метода обработки точек.
    
    Raises
    ------
    EmptyPointsListException
        Если список точек пуст
    InvalidMethodException
        Если метод неизвестен
    InsufficientPointsException
        Если точек недостаточно для метода
    """
    if not points:
        raise EmptyPointsListException()
    
    if method == "original":
        return process_all_points(points)
    elif method == "sequential":
        return process_sequential(points)
    elif method == "min_sum":
        return process_with_min_point(points, use_sum=True)
    elif method == "min_x":
        return process_with_min_point(points, use_sum=False)
    else:
        raise InvalidMethodException(method)


def process_all_points(points):
    """Оригинальный алгоритм."""
    result = []
    
    for p in points:
        try:
            closest = find_closest(p, points)
            if closest:
                new_point = add_two_points(p, closest)
            else:
                new_point = p
        except InsufficientPointsException:
            new_point = p
        
        result.append(new_point)
    
    return result


def process_sequential(points):
    """Последовательный алгоритм."""
    if not points:
        raise EmptyPointsListException()
    
    result = []
    n = len(points)
    
    for i in range(n):
        next_point = points[(i + 1) % n]
        result.append(add_two_points(points[i], next_point))
    
    return result


def process_with_min_point(points, use_sum=True):
    """Алгоритм с минимальной точкой."""
    if not points:
        raise EmptyPointsListException()
    
    try:
        if use_sum:
            special_point = min(points, key=lambda p: p[0] + p[1])
        else:
            special_point = min(points, key=lambda p: (p[0], p[1]))
        
        return [add_two_points(p, special_point) for p in points]
    
    except ValueError as e:
        raise EmptyPointsListException() from e