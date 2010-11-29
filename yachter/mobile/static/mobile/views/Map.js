Y.views.Map = Ext.extend(Ext.Component, {
    title: "Map",
    iconCls: "maps",
    baseCls: "x-map",
    monitorOrientation: true,
    
    initialView: {
        zoom: 11,
        center: {lat:-36.804, lon:174.781}
    },

    map: null,

    initComponent : function() {
        this.scroll = false;
        this._markers = [];
        
        if(!(window.google || {}).maps){
            this.html = 'GMaps API is required';   
            throw Error("GMaps API is required");
        }
        
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

        var latlng = new gm.LatLng(this.initialView.center.lat, this.initialView.center.lon);
        var mapOptions = {
            zoom: this.initialView.zoom,
            center: latlng,
            mapTypeId: gm.MapTypeId.TERRAIN,
            disableDefaultUI: true
        };
        if (this.el && this.el.dom && this.el.dom.firstChild) {
            Ext.fly(this.el.dom.firstChild).remove();
        }
        this.map = new gm.Map(this.el.dom, mapOptions);
                        
        this.fireEvent('maprender', this, this.map);
        
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
    }
});

Ext.reg('YMap', Y.views.Map);
