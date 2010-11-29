Y.views.Map = Ext.extend(Ext.Component, {
    title: "Map",
    iconCls: "maps",
    baseCls: "x-map",
    monitorOrientation: true,
    
    initialView: {
        zoom: 12,
        center: {lat: -36.827, lon: 174.780}
    },

    map: null,

    initComponent : function() {
        this.scroll = false;
        
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

        Ext.Ajax.request({
            url: 'stations/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                var mapPanel = this;
                
                var features = [];
                for (var i=0; i<data['stations'].length; i++) {
                    var station = data['stations'][i];

                    var marker = new gm.Marker({
                        position: new gm.LatLng(station.location[1], station.location[0]),
                        flat: true,
                        title: station.name,
                        map: this.map
                    });

                    var ob = station.latest;
                    if (ob) {
                        marker.YStationId = station.id; 
                        gm.event.addListener(marker, 'click', Ext.createDelegate(function() {
                            mapPanel.fireEvent('stationselect', mapPanel, this.YStationId);
                        }, marker));
                    };
                }
            },
            failure: function(response, opts) {
                console.log('loading stations: got status:', response.status);
            }
        });
    }
});

Ext.reg('YMap', Y.views.Map);
