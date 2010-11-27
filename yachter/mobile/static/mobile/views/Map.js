Y.views.Map = Ext.extend(Ext.Component, {
    title: "Map",
    iconCls: "maps",
    
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
                
        this.addEvents ( 
            'maprender'
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
        var me = this,
            po = window.org.polymaps;
        
        if (po) {
            me.map = po.map()
                .container(me.el.dom.appendChild(po.svg("svg")))
                .center(me.initialView.center)
                .zoom(me.initialView.zoom)
                .add(po.touch())
                .add(po.interact());

            me.map.add(po.image()
                .url(po.url("http://{S}tile.cloudmade.com"
                + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
                + "/998/256/{Z}/{X}/{Y}.png")
                .hosts(["a.", "b.", "c.", ""])));                
                            
            me.fireEvent('maprender', me, me.map);
        }
        
    }
});

Ext.reg('YMap', Y.views.Map);
