window.Y = window.Y || {};

Y.ObservationPanel = Ext.extend(Ext.Panel, {
    cls: "observation",
    fullscreen: true,
    modal: true,
    floating: true,
    hideOnMaskTap: true,
    ui: 'light',
    map: null,
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
        }],
        dock: 'top'
    }],
    initComponent : function() {
        Y.ObservationPanel.superclass.initComponent.call(this);

        var backButton = this.dockedItems.get(0).items.get(0); 
        backButton.on('tap', function() {
            this.hide('slide');
        }, this);

        Ext.Ajax.request({
            url: 'observations/latest/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                var panel = this;
                
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
                                var ob = this.feature.data.properties.observation;
                                panel.update(ob);
                                panel.dockedItems.get(0).setTitle(ob.station_name);
                                panel.show('slide');
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
                this.map.map.add(obsLayer);
            },
            failure: function(response, opts) {
                console.log('loading observations: got status:', response.status);
            }
        });
    }
});

