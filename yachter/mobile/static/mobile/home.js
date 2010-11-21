Ext.regModel('Tide', {
    idProperty: 'id',
    fields: [
        {name:'time', type:'date'}, 
        {name:'height', type:'float'}, 
        {name:'type', type:'string'},
        {name:'id', type:'string'},
    ]
});
var map;

Ext.setup({
    tabletStartupScreen: 'tablet_startup.png',
    phoneStartupScreen: 'phone_startup.png',
    icon: 'icon.png',
    glossOnIcon: false,
    onReady: function() {
        map = new Ext.PolyMap({
            title: 'Map',
            iconCls: 'map',
            mapOptions: {
                zoom: 11,
                center: {lat:-36.73, lon:174.77}
            }
        });
        
        var observationPanel = new Ext.Panel({
            cls: "observation",
            fullscreen: true,
            modal: true,
            floating: true,
            hideOnMaskTap: true,
            ui: 'light',
            tpl: new Ext.XTemplate(
                '<tpl for=".">',
                    '{time}',
                    '<ul>',
                        '<li>Wind: {wind_speed} kn {wind_direction}&deg;</li>',
                        '<li>Gust: {gust_speed} kn</li>',
                        '<li>Temperature: {temp}&deg;</li>',
                        '<li>Pressure: {pressure} hPa</li>',
                    '</ul>',
                '</tpl>'
            ),
            dockedItems: [{
                xtype: 'toolbar',
                ui: 'light',
                title: 'Observation',
                items: [{
                    text: 'Back',
                    ui: 'back',
                    handler: function(button, event) {
                        console.log("back!");
                        observationPanel.hide();
                    }
                }],
                dock: 'top'
            }]

        });

        Ext.Ajax.request({
            url: 'observations/latest/',
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                
                var po = org.polymaps;
                var obsLayer = po.geoJson()
                    .on('load', function(e) {
                        for (var i = 0; i < e.features.length; i++) {
                            var f = e.features[i];
                            var c = n$(f.element);
                            var g = c.parent().add("svg:g", c);
                            
                            g.attr("transform", "translate(" + c.attr("cx") + "," + c.attr("cy") + ")");
                            
                            g.add('svg:circle')
                                .attr('r', f.data.properties.observation.gust_speed / 2)
                                .attr('opacity', 0.5)
                                .attr('class', 'gust_speed');
                            g.add(c
                                .attr('r', f.data.properties.observation.wind_speed / 2)
                                .attr('opacity', 0.5)
                                .attr('cx', null)
                                .attr('cy', null)
                                .attr('class', 'wind_speed'));
                            
                            g.add("svg:title").text(f.data.properties.label);

                            g.on("mousedown", function() {
                                console.log('mousedown: this=', this, this.feature);
                                //debugger;
                                var ob = this.feature.data.properties.observation;
                                observationPanel.update(ob);
                                observationPanel.dockedItems.get(0).setTitle(ob.station_name);
                                observationPanel.show('slide');
                            });

                            // make the feature element class the <g>
                            g.element.feature = f;
                            f.element = g.element;
                        }
                    });
                
                var features = [];
                for (var i=0; i<data['results'].length; i++) {
                    var ob = data['results'][i];
                    var position = {lat:ob.station_location[1], lon:ob.station_location[0]};

                    var rotate = Math.abs(360 - ob['wind_direction'] - 180);
                    var scale = 1.0;
                    var text = Math.round(ob['wind_speed']) + 'kn gusting ' + Math.round(ob['gust_speed']) + 'kn';

                    var obFeature = {
                        "geometry": {
                            "coordinates": ob.station_location,
                            "type": "Point"
                        },
                        "type": "Feature",
                        "id": ob.id,
                        "properties": {
                            "observation": ob,
                            "label": text
                        }
                    };
                    features.push(obFeature);
                }
                obsLayer.features(features);
                map.map.add(obsLayer);
            },
            failure: function(response, opts) {
                console.log('loading observations: got status:', response.status);
            }
        });

        var tidePanel = new Ext.Panel({
            title: 'Tides',
            cls: 'tides',
            scroll: 'vertical',
            iconCls: 'info',
            
            items: new Ext.DataView({
                store: new Ext.data.JsonStore({
                    model: 'Tide',
                    proxy: {
                        type: 'ajax',
                        url: 'tides/',
                        reader: {
                            type: 'json',
                            root: 'results',
                            idProperty: 'id'
                        }
                    },
                    root: 'results',
                    autoLoad: true
                }),
                tpl: new Ext.XTemplate(
                    '<tpl for=".">',
                        '<div class="tide">',
                            '<div class="tide-content">',
                                '<h2>{time}</h2>',
                                '<p>{type}, {height}m</p>',
                            '</div>',
                        '</div>',
                    '</tpl>'
                ),
                autoHeight: true,
                multiSelect: true,
                itemSelector:'div.tide-content',
                emptyText: 'No tides to display'
            })            
        });

        var panel = new Ext.TabPanel({
            tabBar: {
                dock: 'bottom',
                layout: {
                    pack: 'center'
                }
            },
            ui: 'light',
            fullscreen: true,
            cardSwitchAnimation: 'slide',
            items: [map, tidePanel]
        });
    }
});