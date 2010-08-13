import math
import os
import shutil
import tempfile
import zipfile

from django.template.loader import render_to_string
from django.utils import simplejson
from django.conf import settings
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

def export_static_html(export_path):
    """ Export the course map as an HTML file, a JS file, and a set of
    JSON files (1x for each course). Drop this into an <iframe> and it
    should all work nicely. """
    from yachter.courses.models import Course, Mark

    assert os.path.exists(export_path), "Export path (%s) must exist" % export_path

    if not os.path.exists(os.path.join(export_path, 'data')):
        os.makedirs(os.path.join(export_path, 'data'))
    
    courses = Course.objects.all()
    for c in courses:
        f = open(os.path.join(export_path, 'data', 'course_%d.json' % c.id), 'wb')
        f.write(simplejson.dumps(c.json) + '\n')
        f.close()
    
    mark_json = {}
    for m in Mark.objects.all():
        mark_json[m.id] = m.json
        
    f = open(os.path.join(export_path, 'data', 'marks.json'), 'wb')
    f.write(simplejson.dumps(mark_json) + '\n')
    f.close()

    context = {
        'courses': courses,
    }
    html = render_to_string('courses/static_list.html', context)
    f = open(os.path.join(export_path, 'course_list.html'), 'wb')
    f.write(html)
    f.close()

    shutil.copy(os.path.join(settings.MEDIA_ROOT, 'course_list.js'), export_path)

def export_static_zip(f):
    """ Export the course-map HTML as a Zip file """
    d = tempfile.mkdtemp()
    try:
        export_static_html(d)
        fzip = zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)
        
        for root,dirs,files in os.walk(d):
            for f in files:
                archive_name = os.path.join(root.replace(d, 'yachter_courses_html'), f)
                fzip.write(os.path.join(root, f), archive_name)
        fzip.close()
    finally:
        shutil.rmtree(d)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
