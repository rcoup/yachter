Y.views.About = Ext.extend(Ext.Panel, {
    title: "About",
    baseCls: "y-about",
    iconCls: "info",
    scroll: "vertical",

    html: [
        '<h1>Yachter Mobile</h1>',
        '<p>Part of the <a href="http://github.com/rcoup/yachter">Yachter</a> ',
            'open source sailing project. Copyright &copy; 2010, Robert Coup. ',
            'Developed for the 2010 <a href="http://www.mixandmash.org.nz/">',
            'Mix & Mash</a> competition.</p>',
        '<h2>Data Sources</h2>',
        '<ul>',
            '<li>Tide Predictions sourced from <a href="http://www.linz.govt.nz/">Land Information New Zealand</a>. Crown Copyright reserved.</li>',
            '<li>Bathymetry sourced from <a href="http://www.linz.govt.nz/">Land Information New Zealand</a> data. Crown Copyright reserved.</li>',
            '<li>Buoy locations sourced from <a href="http://www.linz.govt.nz/">Land Information New Zealand</a> data. Crown Copyright reserved.</li>',
            '<li>Inshore marine weather forecasts sourced from <a href="http://www.metservice.co.nz/">MetService</a>.</li>',
            '<li>Weather station data sourced from:',
                '<ul>',
                    '<li><a href="http://www.wunderground.com">Weather Underground, Inc.</a></li>',
                    '<li><a href="http://www.rnzys.org.nz">Royal NZ Yacht Squadron</a></li>',
                '</ul>',
            '</li>',
        '<ul>',
        '<h2>Disclaimer</h2>',
        '<p>Maps are not to be used for navigation! Tide data is not official.</p>',
        '<p>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ',
            'ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ',
            'WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE ',
            'DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR DATA SOURCES BE LIABLE FOR ANY ',
            'DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES ',
            '(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; ',
            'LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ',
            'ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT ',
            '(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS ',
            'SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</p>'
    ].join('')
});

Ext.reg('YAbout', Y.views.About);
