/**
 * @class Ext.PolyMap
 * @extends Ext.Component
 *
 * <p>Wraps a Polymaps Map in an Ext.Component.</p>
 *
 * @xtype map
 */
Ext.PolyMap = Ext.extend(Ext.Component, {
    /**
     * @cfg {String} baseCls
     * The base CSS class to apply to the Maps's element (defaults to <code>'x-map'</code>).
     */
    baseCls: 'x-map',

    /**
     * @cfg {Boolean} useCurrentLocation
     * Pass in true to center the map based on the geolocation coordinates.
     */
    useCurrentLocation: false,
    
    /**
     * @cfg {Object} mapOptions
     * MapOptions as specified by the Google Documentation:
     * http://code.google.com/apis/maps/documentation/v3/reference.html
     */

    /**
     * @type {google.maps.Map}
     * The wrapped map.
     */
    map: null,

    /**
     * @type {Ext.util.GeoLocation}
     */
    geo: null,

    /**
     * @cfg {Boolean} maskMap
     * Masks the map (Defaults to false)
     */
    maskMap: false,
    /**
     * @cfg {Strng} maskMapCls
     * CSS class to add to the map when maskMap is set to true.
     */
    maskMapCls: 'x-mask-map',


    initComponent : function() {
        this.mapOptions = this.mapOptions || {};
        
        this.scroll = false;
        
        if(!(window.org || {}).polymaps){
            this.html = 'Polymaps API is required';   
        }
        else if (this.useCurrentLocation) {
            this.geo = this.geo || new Ext.util.GeoLocation({autoLoad: false});
            this.geo.on({
                locationupdate : this.onGeoUpdate,
                locationerror : this.onGeoError, 
                scope : this
            });
        }
        
        Ext.PolyMap.superclass.initComponent.call(this);
                
        this.addEvents ( 
            /**
             * @event maprender
             * @param {Ext.PolyMap} this
             * @param {org.polymaps.Map} map The rendered Polymaps instance
             */     
            'maprender',
        
            /**
             * @event move
             * @param {Ext.PolyMap} this
             * @param {org.polymaps.Map} map The rendered Polymaps instance
             * @param {Object} center The current LatLng center of the map
             */     
            'move'
        );
        
        if (this.geo){
            this.on({
                activate: this.onUpdate,
                scope: this,
                single: true
            });
            this.geo.updateLocation();
        }
        
    },
    
    // @private    
    onRender : function(container, position) {
        Ext.PolyMap.superclass.onRender.apply(this, arguments);
        this.el.setDisplayMode(Ext.Element.OFFSETS);        
    },
    
     // @private
    afterRender : function() {
        Ext.PolyMap.superclass.afterRender.apply(this, arguments);
        this.renderMap();
    },
    
    // @private
    onResize : function( w, h) {
        Ext.PolyMap.superclass.onResize.apply(this, arguments);
        if (this.map) {
            this.map.resize();
        }
    },
    
    afterComponentLayout : function() {
        if (this.maskMap && !this.mask) {
            this.el.mask(null, this.maskMapCls);
            this.mask = true;
        }
    },
    
    renderMap : function(){
        var me = this,
            po = window.org.polymaps;
        
        if (po) {
            if (Ext.is.iPad) {
                Ext.applyIf(me.mapOptions, {
                    navigationControlOptions: {
                        style: gm.NavigationControlStyle.ZOOM_PAN
                    }
                });
            }
                
            Ext.applyIf(me.mapOptions, {
                center: {lat:37.381592, lon:-122.135672}, // Palo Alto
                zoom: 12,
            });
            
            if (me.maskMap && !me.mask) {
                me.el.mask(null, this.maskMapCls);
                me.mask = true;
            }
    
            if (me.el && me.el.dom && me.el.dom.firstChild) {
                Ext.fly(me.el.dom.firstChild).remove();
            }
        
            if (me.map) {
                gm.event.clearInstanceListeners(me.map);
            }
            
            me.map = po.map()
                .container(me.el.dom.appendChild(po.svg("svg")))
                .center(me.mapOptions.center)
                .zoom(me.mapOptions.zoom)
                .add(po.touch())
                .add(po.interact());

            me.map.add(po.image()
                .url(po.url("http://{S}tile.cloudmade.com"
                + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
                + "/998/256/{Z}/{X}/{Y}.png")
                .hosts(["a.", "b.", "c.", ""])));                
                            
            me.map.on('move', Ext.createDelegate(me.onMove, me));
            
            me.fireEvent('maprender', me, me.map);
        }
        
    },

    onGeoUpdate : function(coords) {
        var center;
        if (coords) {
            center = this.mapOptions.center = {lat:coords.latitude, lon:coords.longitude};
        }
        
        if (this.rendered) {
            this.update(center);
        }
        else {
            this.on('activate', this.onUpdate, this, {single: true, data: center});
        }
    },
    
    onGeoError : function(geo){
          
    },

    onUpdate : function(map, e, options) {
        this.update((options || {}).data);
    },
    
    
    /**
     * Moves the map center to the designated coordinates hash of the form:
<code><pre>
 { latitude : 37.381592,
  longitude : -122.135672
  }</pre></code>
     * @param {Object} coordinates Object representing the desired Latitude and
     * longitude upon which to center the map
     */
    update : function(coordinates) {
        var me = this, 
            po = org.polymaps;

        if (po) {
            coordinates = coordinates || me.coords || {lat:37.381592, lon:-122.135672};
            
            if (coordinates && 'longitude' in coordinates) {
                coordinates = {lat:coordinates.latitude, lon:coordinates.longitude};
            }
            
            if (!me.hidden && me.rendered) {
                me.map || me.renderMap();
                if (me.map && coordinates) {
                   me.map.center(coordinates);
                }
            }
            else {
                me.on('activate', me.onUpdate, me, {single: true, data: coordinates});
            }
        }
    },
    
    // @private
    onMove  : function() {
        this.mapOptions.zoom = (this.map ? this.map.zoom() : this.mapOptions.zoom) || 10;
        this.mapOptions.center = this.map ? this.map.center() : this.mapOptions.center;
            
        this.fireEvent('viewchange', this, this.map, this.mapOptions.zoom);
    },
    
    getState : function(){
        return this.mapOptions;  
    },
    
    // @private    
    onDestroy : function() {
        Ext.destroy(this.geo);
        if (this.maskMap && this.mask) {
            this.el.unmask();
        }
        /*
        if (this.map && (window.google || {}).maps) {
            google.maps.event.clearInstanceListeners(this.map);
        }
        */
        Ext.PolyMap.superclass.onDestroy.call(this);
    }
});

Ext.reg('polymap', Ext.PolyMap);