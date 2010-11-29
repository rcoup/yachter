Ext.regController("main", {

    /**
     * Renders the Viewport. This
     * is only expected to be called once - at application startup. This is initially called inside
     * the app.js launch function.
     */
    initial: function() {
        window.Y.appMainController = this;
        
        this.mapView = this.render({
            xtype: 'YMap',
            listeners: {
                scope : this,
                stationselect: this.onSelected
            }
        });
        this.tideChartView = this.render({
            xtype: 'YTideChart'
        }, false);
        this.forecastView = this.render({
            xtype: 'YForecast'
        }, false);
        this.aboutView = this.render({
            xtype: 'YAbout'
        }, false);

        this.tabPanel = new Ext.TabPanel({
            tabBar: {
                dock: 'bottom',
                layout: {
                    pack: 'center'
                }
            },
            ui: 'light',
            fullscreen: true,
            cardSwitchAnimation: 'slide',
            items: [
                this.mapView, 
                this.tideChartView,
                this.forecastView,
                this.aboutView
            ]
        });

        this.stationView = this.render({
            xtype: 'YStation', 
            map: this.mapView,
            hidden: true
        });
    },

    /**
     * Shows a details overlay for a given Station. This creates a single 
     * reusable view and simply updates it each time a Station is tapped on.
     */
    showStation: function(options) {
        this.stationView.setStation(options.id);
        this.stationView.show();
    },
    
    /**
     * @private
     * Causes the Station details overlay to be shown if there is a Station selected
     */
    onSelected: function(selectionModel, station_id) {
        if (station_id) {
            this.showStation({
                id: station_id
            });
        }
    }
});