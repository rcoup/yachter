Y.views.Station = Ext.extend(Ext.Panel, {
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
        }],
        dock: 'top'
    }],
    initComponent : function() {
        Y.views.Station.superclass.initComponent.call(this);

        var backButton = this.dockedItems.get(0).items.get(0); 
        backButton.on('tap', function() {
            this.hide('slide');
        }, this);
    },
    setTitle : function(text) {
        this.dockedItems.get(0).setTitle(text);
    },
    setStation : function(id) {
        this.setTitle("Loading...");
        this.setLoading(true);
        
        Ext.Ajax.request({
            url: 'stations/' + id + '/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                
                this.setTitle(data.name);
                if (data.latest) {
                    this.update(data.latest);
                }
                this.setLoading(false);
            },
            failure: function(response, opts) {
                console.log('loading station', id, ': got status:', response.status);
                this.setLoading(false);
            }
        });
    }
});

Ext.reg('YStation', Y.views.Station);
