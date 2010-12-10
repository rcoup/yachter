Y.views.About = Ext.extend(Ext.Panel, {
    title: "About",
    baseCls: "y-about",
    iconCls: "info_plain",
    scroll: "vertical",

    html: [
        '<h1>Yachter Mobile</h1>',
        '<p>Part of the <a href="http://github.com/rcoup/yachter">Yachter</a> ',
            'open source sailing project. Copyright &copy; 2010, Robert Coup. ',
            'Developed for the 2010 <a href="http://www.mixandmash.org.nz/">',
            'Mix & Mash</a> competition.</p>',
        '<h2>Data Sources</h2>',
        '<ul>',
            '<li>Base map Copyright 2010 <a href="http://www.cloudmade.com/">CloudMade</a>, <a href="www.openstreetmap.org">OpenStreetMap</a> contributors, CCBYSA. "Pale Dawn" cartography by <a href="http://www.stamen.com">Stamen</a>.</li>',
            '<li>Tide Predictions sourced from <a href="http://www.linz.govt.nz/">Land Information New Zealand</a>. Crown Copyright reserved.</li>',
            '<li>Bathymetry &amp; buoy locations digitised from <a href="http://www.linz.govt.nz/">Land Information New Zealand</a> charts. Crown Copyright reserved.</li>',
            '<li>Inshore marine weather forecasts sourced from <a href="http://www.metservice.co.nz/">MetService</a>.</li>',
            '<li>Weather station data sourced from:',
                '<ul>',
                    '<li><a href="http://www.wunderground.com">Weather Underground, Inc.</a></li>',
                    '<li><a href="http://www.rnzys.org.nz">Royal NZ Yacht Squadron</a></li>',
                '</ul>',
            '</li>',
        '<ul>',
        '<h2>Warnings</h2>',
        '<p><strong>Maps are not to be used for navigation!</strong> Tide data &amp; predictions are <strong>not</strong> official.</p>',
        '<p>This software is provided by the copyright holders and contributors "as is" and ',
            'any express or implied warranties, including, but not limited to, the implied ',
            'warranties of merchantability and fitness for a particular purpose are ',
            'disclaimed. In no event shall the authors or data sources be liable for any ',
            'direct, indirect, incidental, special, exemplary, or consequential damages ',
            '(including, but not limited to, procurement of substitute goods or services; ',
            'loss of use, data, or profits; or business interruption) however caused and ',
            'on any theory of liability, whether in contract, strict liability, or tort ',
            '(including negligence or otherwise) arising in any way out of the use of this ',
            'software, even if advised of the possibility of such damage.</p>'
    ].join('')
});

Ext.reg('YAbout', Y.views.About);
