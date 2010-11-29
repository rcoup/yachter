Y.views.Map = Ext.extend(Ext.Component, {
    title: "Map",
    iconCls: "maps",
    baseCls: "x-map",
    monitorOrientation: true,
    
    initialView: {
        zoom: 11,
        center: {lat:-36.804, lon:174.781}
    },
    GEO_LEVEL: 14,

    map: null,

    initComponent : function() {
        this.scroll = false;
        this._markers = [];
        this._geoMarkers = [];
        
        if(!(window.google || {}).maps){
            console.error("GMaps API is required");
            Ext.Msg.alert("Mapping", "Google Maps is required");
            throw Error("GMaps API is required");
        }

        this.geo = new Ext.util.GeoLocation({
            autoUpdate: true
            //allowHighAccuracy: true
        });
        this.geo.on({
            locationupdate : this.onGeoUpdate,
            locationerror : this.onGeoError, 
            scope : this
        });
        
        Y.views.Map.superclass.initComponent.call(this);

        this.addManagedListener(this, 'orientationchange', function(orientation, w, h) {
            this.map && google.maps.event.trigger(this.map, 'resize'); 
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
            google.maps.event.trigger(this.map, 'resize') 
        }
    },
    
    renderMap : function(){
        var gm = google.maps;

        var hosts = ['a.', 'b.', 'c.', ''];
        var cloudmadeMapOptions = {
            getTileUrl: function(coord, zoom) {
                return "http://" + hosts[(Math.abs(zoom) + coord.y + coord.x) % hosts.length]
                    + "tile.cloudmade.com/f780b36762004b66955ad380b798665a/998/256/"
                    + zoom + "/" + coord.x + "/" + coord.y + ".png";
            },
            tileSize: new gm.Size(256, 256),
            isPng: true,
            maxZoom: 18
        };
        var cloudmadeMapType = new gm.ImageMapType(cloudmadeMapOptions);

        var latlng = new gm.LatLng(this.initialView.center.lat, this.initialView.center.lon);
        var mapOptions = {
            zoom: this.initialView.zoom,
            center: latlng,
            disableDefaultUI: true
        };
        if (this.el && this.el.dom && this.el.dom.firstChild) {
            Ext.fly(this.el.dom.firstChild).remove();
        }
        this.map = new gm.Map(this.el.dom, mapOptions);
        this.map.mapTypes.set('osm_cloudmade', cloudmadeMapType);
        this.map.setMapTypeId('osm_cloudmade');
                        
        this.fireEvent('maprender', this, this.map);
        
        gm.event.addListener(this.map, 'zoom_changed', Ext.createDelegate(this.onZoom, this));
        
        this.update();
    },
    
    update : function() {
        var gm = google.maps;
        
        Ext.Ajax.request({
            url: 'stations/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                var mapPanel = this;
                
                while(this._markers.length) {
                    this._markers.pop().setMap(null);
                }
                
                for (var i=0; i<data['stations'].length; i++) {
                    var station = data['stations'][i];

                    var ob = station.latest;
                    var marker;
                    if (ob) {
                        marker = new WindArrow({
                            position: new gm.LatLng(station.location[1], station.location[0]),
                            title: station.name,
                            rotation: (ob.wind_direction + 180) % 360,
                            color: 'red',
                            opacity: 1.0,
                            scale: 1 + Math.max((ob.wind_speed - 5) / 20, 0),
                            map: this.map
                        });
                    } else {
                        marker = new gm.Marker({
                            position: new gm.LatLng(station.location[1], station.location[0]),
                            flat: true,
                            title: station.name,
                            icon: '/static/mobile/images/redblank.png',
                            map: this.map
                        });
                    }
                    marker.YStationId = station.id; 
                    gm.event.addListener(marker, 'click', Ext.createDelegate(function() {
                        mapPanel.fireEvent('stationselect', mapPanel, this.YStationId);
                    }, marker));
                    this._markers.push(marker);
                }
            },
            failure: function(response, opts) {
                console.log('loading stations: got status:', response.status);
            }
        });
    },
    
    onZoom : function() {
        var z = this.map.getZoom();
        var zo = this._oldZoom;
        this._oldZoom = z;

        if (zo) {
            if (zo >= this.GEO_LEVEL && z >= this.GEO_LEVEL) {
                return;
            } else if (zo < this.GEO_LEVEL && z < this.GEO_LEVEL) {
                return;
            }
        }
        var show = (z >= this.GEO_LEVEL);
        for (var i=0; i<this._geoMarkers.length; i++) {
            this._geoMarkers[i].setVisible(show);
        }
    },
    onGeoUpdate: function(geo) {
        //console.log("geo-locationupdate:", geo);
        var gm = google.maps;
        
        if (this.map) {
            // prune old markers
            while (this._geoMarkers.length > 99) {
                this._geoMarkers.shift().setMap(null);
            }
            if (this._geoCurrentMarker) {
                this._geoCurrentMarker.setIcon('/static/mobile/images/orangedot.png');
                this._geoCurrentMarker.setVisible(this.map.getZoom() >= this.GEO_LEVEL);
                this._geoCurrentMarker.setZIndex(-2);
                this._geoMarkers.push(this._geoCurrentMarker);
            }
        
            this._geoCurrentMarker = new gm.Marker({
                position: new gm.LatLng(geo.latitude, geo.longitude),
                flat: true,
                icon: '/static/mobile/images/reddot.png',
                clickable: false,
                zIndex: -1,
                map: this.map
            });
        }
    },
    onGeoError: function(geo,
                        bTimeout, 
                        bPermissionDenied, 
                        bLocationUnavailable, 
                        message) {
        console.error("geo-locationerror:", geo, bTimeout, bPermissionDenied, bLocationUnavailable, message);
        Ext.Msg.alert("GeoLocation", "No GPS for you!");
    }
});

Ext.reg('YMap', Y.views.Map);
