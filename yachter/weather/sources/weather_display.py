from __future__ import with_statement
import urllib2
import unittest
from datetime import datetime
import os
import time

import pytz

class WeatherDisplay(object):
    def __init__(self, tz_id):
        self.timezone = pytz.timezone(tz_id)
        
    def query(self, station_baseurls):
        for station_baseurl in station_baseurls:
            url = os.path.join(station_baseurl, "clientraw.txt") 
            resp = urllib2.urlopen(url)
            
            doc = resp.read().strip().split(' ')
            yield self._build_results(station_baseurl, doc)
    
    def _build_results(self, station_id, doc):
        return {
            'station_id': station_id,
            'time': self.time(doc),
            'wind_speed': float(doc[1]),
            'gust_speed': float(doc[2]),
            'wind_direction': int(doc[3]),
            'temp': float(doc[4]),
            'pressure': float(doc[6]),
        }
    
    def time(self, doc):
        H,M,S = doc[29:32]
        d,m,y = doc[74].split('/')
        
        return datetime(int(y), int(m), int(d), int(H), int(M), int(S), tzinfo=self.timezone)

class TestWeatherDisplay(unittest.TestCase):
    RNZYS = "http://weather.rnzys.org.nz/"

    def setUp(self):
        test_file_path = os.path.join(os.path.split(__file__)[0], 'test_data', 'weather_display.txt')
        with open(test_file_path, 'rb') as test_file:
            self.doc = test_file.read().strip().split(' ')
        self.source = WeatherDisplay('Pacific/Auckland')
    
    def test_time(self):
        t = self.source.time(self.doc)
        self.assertEqual(t, datetime(2010,11,13,13,54,50, tzinfo=pytz.timezone('Pacific/Auckland')))
    
    def test_results(self):
        results = self.source._build_results('TEST', self.doc)
        print results
        
        self.assertEqual(results, {
            'station_id': 'TEST',
            'time': datetime(2010,11,13,13,54,50, tzinfo=pytz.timezone('Pacific/Auckland')),
            'wind_speed': 6.7,
            'wind_direction': 270,
            'gust_speed': 7.6,
            'temp': 21.6,
            'pressure': 1026.2,
        })
    