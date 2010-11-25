from __future__ import with_statement
import urllib
import urllib2
import unittest
from datetime import datetime
import os
import time

import pytz
from lxml import etree

class WindNZ(object):
    """ Grab data from the XML used to power http://www.wind.co.nz/ """
    
    URL = "http://www.wind.co.nz/nonhtml/getxml.php"
    MULTIPLE_STATIONS = True
    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)'
    
    def __init__(self, **params):
        self.region_id = params['region_id']
    
    def query(self, station_ids=None):
        url = self.URL + "?" + urllib.urlencode({'regionid': str(self.region_id)}) 
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', self.USER_AGENT)]
        resp = opener.open(url)
        xml_doc = etree.parse(resp)

        if station_ids is None:
            station_ids = self.get_station_ids(xml_doc)

        return self._build_results(xml_doc, station_ids)

    def _build_results(self, xml_doc, station_ids):
        for station_id in station_ids:
            station_xml = self.station(xml_doc, station_id)
            if station_xml is not None:
                results = {
                    'station_id': station_id,
                    'time': self.time(station_xml),
                }
                if results['time']:
                    for e in ('temp', 'wind_speed', 'wind_direction', 'gust_speed', 'pressure'):
                        v = getattr(self, e)(station_xml)
                        if v is not None:
                            results[e] = v
                    if len(results) > 2:
                        yield results

    def get_station_ids(self, xml_doc):
        return map(str, xml_doc.xpath('/winddata/sensor/@sensorid'))
    
    def station(self, xml_doc, station_id):
        sensors = xml_doc.xpath('/winddata/sensor[@sensorid=%s]' % station_id)
        if len(sensors):
            return sensors[0]
        
    def temp(self, station_xml):
        e = station_xml.xpath('obtb/ob[@dtid=3]/@d')
        if e:
            return float(e[0])
    
    def wind_speed(self, station_xml):
        e = station_xml.xpath('obtb/ob[@dtid=2]/@d')
        if e:
            return float(e[0])
    
    def wind_direction(self, station_xml):
        e = station_xml.xpath('obtb/ob[@dtid=1]/@d')
        if e:
            return int(e[0])

    def gust_speed(self, station_xml):
        e = station_xml.xpath('obtb/ob[@dtid=4]/@d')
        if e:
            return float(e[0])

    def pressure(self, station_xml):
        e = station_xml.xpath('obtb/ob[@dtid=6]/@d')
        if e:
            return float(e[0])

    def time(self, station_xml):
        e = station_xml.xpath('obtb/ob/@t')
        if e:
            return datetime(tzinfo=pytz.timezone('Pacific/Auckland'), *(time.strptime(e[0], '%Y%m%d%H%M%S')[0:6]))

class TestWindNZ(unittest.TestCase):
    def setUp(self):
        test_file_path = os.path.join(os.path.split(__file__)[0], 'test_data', 'wind_nz.xml')
        with open(test_file_path, 'rb') as test_file:
            self.xml_doc = etree.parse(test_file)
        self.source = WindNZ(region_id=51)
    
    def test_station(self):
        s = self.source.station(self.xml_doc, 30)
        self.assert_(len(s))
        self.assertEqual(s.get('location'), 'Bean Rock (bea)')

        s = self.source.station(self.xml_doc, 9999)
        self.assertEqual(s, None)
    
    def test_temp(self):
        s = self.source.station(self.xml_doc, 11)
        t = self.source.temp(s)
        self.assertEqual(t, 20.0)

        s = self.source.station(self.xml_doc, 30)
        t = self.source.temp(s)
        self.assertEqual(t, None)
    
    def test_wind_speed(self):
        s = self.source.station(self.xml_doc, 30)
        w = self.source.wind_speed(s)
        self.assertEqual(w, 11.0)

        s = self.source.station(self.xml_doc, 13)
        w = self.source.wind_speed(s)
        self.assertEqual(w, None)

    def test_gust_speed(self):
        s = self.source.station(self.xml_doc, 30)
        w = self.source.gust_speed(s)
        self.assertEqual(w, 16.0)

        s = self.source.station(self.xml_doc, 13)
        w = self.source.gust_speed(s)
        self.assertEqual(w, None)
        
    def test_wind_direction(self):
        s = self.source.station(self.xml_doc, 30)
        w = self.source.wind_direction(s)
        self.assertEqual(w, 230)

        s = self.source.station(self.xml_doc, 13)
        w = self.source.wind_direction(s)
        self.assertEqual(w, None)
    
    def test_pressure(self):
        s = self.source.station(self.xml_doc, 23)
        p = self.source.pressure(s)
        self.assertEqual(p, 1028.0)

        s = self.source.station(self.xml_doc, 30)
        p = self.source.pressure(s)
        self.assertEqual(p, None)
    
    def test_time(self):
        s = self.source.station(self.xml_doc, 30)
        t = self.source.time(s)
        self.assertEqual(t, datetime(2010,11,13,13,01,0, tzinfo=pytz.timezone('Pacific/Auckland')))
    
    def test_get_station_ids(self):
        id_list = self.source.get_station_ids(self.xml_doc)
        self.assertEqual(len(id_list), 10)
        self.assert_('30' in id_list)
        self.assertEqual(type(id_list[0]), str)
    
    def test_results(self):
        results = list(self.source._build_results(self.xml_doc, ('30','13','11')))
        print results
        
        self.assertEqual(len(results), 3)
        r = results[0]
        self.assertEqual(r, {
            'station_id': '30',
            'time': datetime(2010,11,13,13,01,0, tzinfo=pytz.timezone('Pacific/Auckland')),
            'wind_speed': 11.0,
            'wind_direction': 230,
            'gust_speed': 16.0,
        })
        
        for k,t in {'station_id':str, 'time':datetime, 'wind_speed':float, 'wind_direction':int, 'gust_speed':float}.items():
            self.assert_(type(r[k]) == t, '%s attribute is of type %s, not %s' % (k, type(r[k]), t))

if __name__ == "__main__":
    import sys
    import pprint
    
    if len(sys.argv) != 2:
        print >>sys.stderr, "USAGE: %s REGIONID" % sys.argv[0]
        sys.exit(2)
    
    w = WindNZ(region_id=sys.argv[1])
    results = list(w.query())
    pprint.pprint(results)
