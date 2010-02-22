import math

from django.contrib.gis.geos import Point

def bearing(p0, p1):
    """
    >>> bearing((0, 0), (0, 1))
    0.0
    >>> bearing((0, 0), (1, 1))
    45.0
    >>> bearing((0, 0), (1, 0))
    90.0
    >>> bearing((0, 0), (1, -1))
    135.0
    >>> bearing((0, 0), (0, -1))
    180.0
    >>> bearing((0, 0), (-1, -1))
    225.0
    >>> bearing((0, 0), (-1, 0))
    270.0
    >>> bearing((0, 0), (-1, 1))
    315.0
    """
    dx = float(p1[0]) - float(p0[0])
    dy = float(p1[1]) - float(p0[1])
    d = math.sqrt(dx**2 + dy**2)
    a_r = math.asin(dy / d)
    a_d = int(a_r / math.pi * 180.0)
    
    if dx >= 0:
        # Quadrant 1/4
        return 90 - a_d
    else:
        # Quadrant 2/3
        return 270 + a_d

def wind_angle_measure(path, wind, target, delta):
    """
    >>> from django.contrib.gis.geos import LineString
    >>> path = LineString((0,0), (0, 100))
    >>> wind_angle_measure(path, 0, 0, 30)
    (1.0, 1)
    >>> wind_angle_measure(path, 0, 180, 30)
    (0.0, 0)
    >>> wind_angle_measure(path, 15, 0, 30)
    (1.0, 1)
    >>> wind_angle_measure(path, 180, 180, 30)
    (1.0, 1)
    >>> wind_angle_measure(path, 165, 180, 30)
    (1.0, 1)
    >>> wind_angle_measure(path, 90, 0, 30)
    (0.0, 0)
    >>> wind_angle_measure(path, 270, 0, 30)
    (0.0, 0)
    >>> wind_angle_measure(path, 270, 90, 30)
    (1.0, 1)
    """
    
    wind_area = (
        (wind + target) % 360.0 - delta,
        (wind + target) % 360.0 + delta,
    )
    
    results = [0.0, 0]
    p_from = Point(*path[0])
    for i,p_to in enumerate(path[1:]):
        p_to = Point(*p_to)
        p_dist = p_from.distance(p_to) # meters
        p_bearing = bearing(p_from.tuple, p_to.tuple)
        
        if (p_bearing >= wind_area[0] and p_bearing <= wind_area[1]) \
                or (p_bearing + 360.0 >= wind_area[0] and p_bearing + 360.0 <= wind_area[1]):
            results[0] += p_dist
            results[1] += 1
        
        p_from = p_to
    
    return (results[0] / path.length, results[1])

if __name__ == "__main__":
    import doctest
    doctest.testmod()
