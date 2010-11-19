from __future__ import with_statement
import urllib2
import unittest
from datetime import datetime
import os
import time
import rfc822

from lxml import etree
import pytz

class WeatherUnderground(object):
    BASE_URL = 'http://api.wunderground.com/weatherstation/WXCurrentObXML.asp'
    
    def query(self, station_ids):
        results = {}
        
        for id in station_ids:
            url = self.BASE_URL + "?ID=" + id
            resp = urllib2.urlopen(url)
            xml_doc = etree.parse(resp)
        
            yield self._build_results(id, xml_doc)
    
    def _build_results(self, station_id, doc):
        result = {
            'station_id': station_id,
            'time': self.time(doc.xpath('/current_observation/observation_time_rfc822/text()')[0]),
            'temp': float(doc.xpath('/current_observation/temp_c/text()')[0]),
            'wind_direction': int(doc.xpath('/current_observation/wind_degrees/text()')[0]),
            'pressure': float(doc.xpath('/current_observation/pressure_mb/text()')[0]),
            'wind_speed': self.to_knots(doc.xpath('/current_observation/wind_mph/text()')[0]),
            'gust_speed': self.to_knots(doc.xpath('/current_observation/wind_gust_mph/text()')[0]),
        }
        return result
    
    def to_knots(self, mph):
        return float(mph) * 0.868976242
    
    def time(self, rfc822_date):
        utctimestamp = rfc822.mktime_tz(rfc822.parsedate_tz(rfc822_date))
        utcdate = datetime.fromtimestamp(utctimestamp, pytz.UTC)
        return utcdate
    
class TestWeatherUnderground(unittest.TestCase):
    STATION_ID = 'IAUCKLAN51'

    def setUp(self):
        test_file_path = os.path.join(os.path.split(__file__)[0], 'test_data', 'wunderground.xml')
        with open(test_file_path, 'rb') as test_file:
            self.doc = etree.parse(test_file)
        self.source = WeatherUnderground()
    
    def test_time(self):
        t = self.source.time('Sat, 13 November 2010 02:50:22 GMT')
        self.assertEqual(t, datetime(2010,11,13,2,50,22, tzinfo=pytz.timezone('Etc/UTC')))
    
    def test_results(self):
        results = self.source._build_results('TEST', self.doc)
        print results
        
        self.assertEqual(results, {
            'station_id': 'TEST',
            'time': datetime(2010,11,13,2,59,21, tzinfo=pytz.UTC),
            'wind_speed': 4.6924717068000001,
            'wind_direction': 289,
            'gust_speed': 11.035998273399999,
            'temp': 21.5,
            'pressure': 1021.6,
        })
        