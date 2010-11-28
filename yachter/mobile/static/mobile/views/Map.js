Y.views.Map = Ext.extend(Ext.Component, {
    title: "Map",
    iconCls: "maps",
    monitorOrientation: true,
    
    initialView: {
        zoom: 11,
        center: {lat: -36.827, lon: 174.780}
    },

    map: null,

    initComponent : function() {
        this.scroll = false;
        
        if(!(window.org || {}).polymaps){
            this.html = 'Polymaps API is required';   
        }
        
        Y.views.Map.superclass.initComponent.call(this);

        this.addManagedListener(this, 'orientationchange', function(orientation, w, h) {
                this.map && this.map.resize();
            }, this);
                                
        this.addEvents ( 
            'maprender',
            'stationselect'
        );
    },
    
    // @private    
    onRender : function(container, position) {
        Y.views.Map.superclass.onRender.apply(this, arguments);
        this.el.setDisplayMode(Ext.Element.OFFSETS);        
    },
    
     // @private
    afterRender : function() {
        Y.views.Map.superclass.afterRender.apply(this, arguments);
        this.renderMap();
    },
    
    // @private
    onResize : function( w, h) {
        Y.views.Map.superclass.onResize.apply(this, arguments);
        if (this.map) {
            this.map.resize();
        }
    },
    
    renderMap : function(){
        var po = window.org.polymaps;
        
        this.map = po.map()
            .container(this.el.dom.appendChild(po.svg("svg")))
            .center(this.initialView.center)
            .zoom(this.initialView.zoom)
            .add(po.touch())
            .add(po.interact());

        this.map.add(po.image()
            .url(po.url("http://{S}tile.cloudmade.com"
            + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
            + "/998/256/{Z}/{X}/{Y}.png")
            .hosts(["a.", "b.", "c.", ""])));                
                        
        this.fireEvent('maprender', this, this.map);

        Ext.Ajax.request({
            url: 'stations/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                var mapPanel = this;
                
                var stationsLayer = po.geoJson()
                    .on('load', function(e) {
                        for (var i = 0; i < e.features.length; i++) {
                            var f = e.features[i];
                            var c = n$(f.element);
                            var g = c.parent().add("svg:g", c);
                            
                            g.attr("transform", "translate(" + c.attr("cx") + "," + c.attr("cy") + ")");
                            
                            var ob = f.data.properties.observation;
                            if (ob) {
                                var rotate = Math.abs(360 - ob['wind_direction'] - 180);
                                var scale = 1.0;
                                var text = Math.round(ob['wind_speed']) + 'kn gusting ' 
                                    + Math.round(ob['gust_speed']) + 'kn';
                            
                                g.add('svg:circle')
                                    .attr('r', ob.gust_speed / 2)
                                    .attr('opacity', 0.5)
                                    .attr('class', 'gust_speed');
                                g.add(c
                                    .attr('r', ob.wind_speed / 2)
                                    .attr('opacity', 0.5)
                                    .attr('cx', null)
                                    .attr('cy', null)
                                    .attr('class', 'wind_speed'));
                            
                                g.add("svg:title").text(text);
                            } else {
                                g.add(c
                                    .attr('r', 5)
                                    .attr('opacity', 0.5)
                                    .attr('cx', null)
                                    .attr('cy', null)
                                    .attr('class', 'no_observation'));
                                g.add("svg:title").text("No observation");
                            }

                            g.on("mousedown", function() {
                                var station_id = this.feature.data.id;
                                mapPanel.fireEvent('stationselect', mapPanel, station_id);
                            });

                            // make the feature element class the <g>
                            g.element.feature = f;
                            f.element = g.element;
                        }
                    });
                
                var features = [];
                for (var i=0; i<data['stations'].length; i++) {
                    var station = data['stations'][i];

                    var stationFeature = {
                        "geometry": {
                            "coordinates": station.location,
                            "type": "Point"
                        },
                        "type": "Feature",
                        "id": station.id,
                        "properties": {
                        }
                    };

                    var ob = station.latest;
                    if (ob) {
                        stationFeature.properties.observation = ob;
                    };
                    features.push(stationFeature);
                }
                stationsLayer.features(features);
                this.map.add(stationsLayer);
            },
            failure: function(response, opts) {
                console.log('loading stations: got status:', response.status);
            }
        });
    }
});

Ext.reg('YMap', Y.views.Map);
