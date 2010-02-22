Yachter - help run better yacht races
=====================================

 * [http://github.com/rcoup/yachter](http://github.com/rcoup/yachter)

Yachter is designed to be a suite of web-based tools to improve how yacht
clubs run and manage their races.

Currently it consists of a Course Manager which:

 * plots courses on an interactive map
 * calculates beats/runs/reaches for different wind conditions
 * produces rankings
 * helps select courses for current conditions

Yachter was developed for the [Ponsonby Cruising Club](www.pcc.org.nz) 
in Auckland, New Zealand.

Yachter is built as a series of Django applications, and uses the
GeoDjango framework to do all its mapping.

License
-------

    Copyright 2010 Robert Coup

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Requirements
------------

 * Python >= 2.4
 * Django >= 1.1
 * PostGIS, GEOS, PostgreSQL, GDAL/OGR, and Proj4, setup as per the 
   [GeoDjango Installation docs](http://geodjango.org/docs/install.html).
 * Django South >= 0.6
 
Quick Start
-----------

 1. Create a PostGIS-enabled database.
 2. Copy `yachter/settings_site.py.sample` to `yachter/settings_site.py`.
 3. Edit it and modify your settings (database, secret key, paths, etc).
 4. Run `python yachter/manage.py syncdb` and `python yachter/manage.py migrate`
    to initialise the database and create an admin user.
 5. Run `python yachter/manage.py runserver` to run the development server.
 6. Visit `http://localhost:8000/` in your browser and log in.

Support, Feedback, Improvements, Patches
----------------------------------------

 * Check out the [Yachter pages](http://github.com/rcoup/yachter) at Github.
 * File improvements/problems/patches in the [Issue tracker](http://github.com/rcoup/yachter/issues)
 * Email Rob at [robert@coup.net.nz](mailto:robert@coup.net.nz)

