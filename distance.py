import math
from exceptions import DistanceCalculationException, InsufficientPointsException


def calc_dist(p1, p2):
    """
    Вычисляет евклидово расстояние между двумя точками.
    
    Raises
    ------
    DistanceCalculationException
        Если произошла ошибка при вычислении
    """
    try:
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    except (TypeError, ValueError) as e:
        raise DistanceCalculationException(p1, p2) from e


def find_closest(target, points):
    """
    Находит ближайшую точку к заданной среди списка точек.
    
    Raises
    ------
    InsufficientPointsException
        Если точек недостаточно
    """
    if len(points) <= 1:
        raise InsufficientPointsException(actual=len(points))
    
    try:
        # Убираем саму точку из списка
        other_points = [p for p in points if p != target]
        
        if not other_points:
            return None
        
        # Ищем точку с минимальным расстоянием
        closest = min(other_points, key=lambda p: calc_dist(target, p))
        return closest
    
    except ValueError as e:
        raise InsufficientPointsException(actual=len(points)) from e