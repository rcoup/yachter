Ext.regModel('Tide', {
    idProperty: 'id',
    fields: [
        {name:'time', type:'date'}, 
        {name:'height', type:'float'}, 
        {name:'type', type:'string'},
        {name:'id', type:'string'},
    ]
});

Ext.setup({
    tabletStartupScreen: 'tablet_startup.png',
    phoneStartupScreen: 'phone_startup.png',
    icon: 'icon.png',
    glossOnIcon: false,
    onReady: function() {
        var map = new Ext.Map({
            title: 'Map',
            useCurrentLocation: true,
            mapOptions: {
                zoom: 12
            }
        });

        var tidePanel = new Ext.Panel({
            title: 'Tides',
            cls: 'tides',
            scroll: 'vertical',
            
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