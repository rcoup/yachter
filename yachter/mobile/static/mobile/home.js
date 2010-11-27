window.Y = window.Y || {};

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
    tabletStartupScreen: '/static/mobile/images/tablet_startup.png',
    phoneStartupScreen: '/static/mobile/images/phone_startup.png',
    fullscreen: true,
    icon: '/static/mobile/images/icon.png',
    glossOnIcon: false,
    statusBarStyle: 'black',
    
    onReady: function() {
        map = new Ext.PolyMap({
            title: 'Map',
            iconCls: 'maps',
            mapOptions: {
                zoom: 11,
                center: {lat: -36.827, lon: 174.780}
            }
        });
        
        var observationPanel = new Y.ObservationPanel({map:map});

        var tideChartPanel = new Y.TideChartPanel({});

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
            items: [map, tideChartPanel]
        });
    }
});