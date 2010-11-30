Y.views.Station = Ext.extend(Ext.Panel, {
    baseCls: "y-station",
    ui: 'light',

    fullscreen: true,
    centered : true,
    scroll: 'vertical',
    monitorOrientation: true,
    monitorResize: true,

    plugins: [new Ext.ux.touch.ListPullRefresh({
        reloadFn: function(cb, scope) {
            if (scope.cmp.stationId) {
                scope.cmp._loadStation(scope.cmp.stationId, Ext.createDelegate(cb, this));
            } else {
                cb.call(this);
            }
        }
    })],
    chartHeight: 150,

    tpl_latest: new Ext.XTemplate(
        '<tpl for=".">',
            '<div class="ob">',
                '<p class="obTime">{time:date("D d M g:ia")}</p>',
                '<ul class="obInfo">',
                    '<li>Wind:&nbsp;{wind_speed}&nbsp;kn {wind_direction}&deg;&nbsp;({wind_compass})</li>',
                    '<li>Gust:&nbsp;{gust_speed}&nbsp;kn</li>',
                    '<li>Temperature:&nbsp;{temp}&deg;C</li>',
                    '<li>Pressure:&nbsp;{pressure}&nbsp;hPa</li>',
                '</ul>',
            '</div>',
        '</tpl>'
    ),
    dockedItems: [{
        xtype: 'toolbar',
        ui: 'light',
        title: 'Station',
        items: [{
            text: 'Back',
            ui: 'back',
        }],
        dock: 'top'
    }],
    initComponent : function() {
        Y.views.Station.superclass.initComponent.call(this);

        this.stationId = null;

        var backButton = this.dockedItems.get(0).items.get(0); 
        backButton.on('tap', function() {
            this.hide('slide');
        }, this);

        this.addManagedListener(this, 'resize', function(w, h) {
                this.windSpeedChart && this.windSpeedChart.setSize(this.width, this.chartHeight, false);
                this.windDirectionChart && this.windDirectionChart.setSize(this.width, this.chartHeight, false);
                this.tempPressureChart && this.tempPressureChart.setSize(this.width, this.chartHeight, false);
            }, this);
        this.addManagedListener(this, 'orientationchange', function(orientation, w, h) {
                this.windSpeedChart && this.windSpeedChart.setSize(this.width, this.chartHeight, false);
                this.windDirectionChart && this.windDirectionChart.setSize(this.width, this.chartHeight, false);
                this.tempPressureChart && this.tempPressureChart.setSize(this.width, this.chartHeight, false);
            }, this);

    },
    afterRender : function() {
        Y.views.Station.superclass.afterRender.apply(this, arguments);
        this.body.setStyle('zIndex', 10);
        var spec = {
            cls: 'station',
            tag: 'div',
            children: [
                {tag:'div', cls:'latest'},
                {tag:'div', cls:'history', children: [
                    {tag:'div', cls:'wind_speed'},
                    {tag:'div', cls:'wind_direction'},
                    {tag:'div', cls:'temp_pressure'}
                ]},
                {tag:'p', cls:'credits'}
            ]
        }
        Ext.DomHelper.append(this.scroller.el.dom, spec);
        this.elLatest = this.body.down('.latest');
        this.elCredits = this.body.down('.credits');
        
        // create charts
        this.chartSeries = {
            windSpeed: {
                id: 'sWindSpeed',
                type: 'line',
                color: '#0000ff',
                marker: {
                    enabled: false,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                }  
            },
            gustSpeed: {
                id: 'sGustSpeed',
                type: 'line',
                color: '#ff0000',
                marker: {
                    enabled: false,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                }  
            },
            direction: {
                id: 'sDirection',
                type: 'line',
                color: '#0000ff',
                marker: {
                    enabled: false,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                }  
            },
            temp: {
                id: 'sTemp',
                type: 'spline',
                color: '#ff0000',
                marker: {
                    enabled: false,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                },
                name: 'temp'
            },
            pressure: {
                id: 'sPressure',
                type: 'spline',
                color: '#0000ff',
                marker: {
                    enabled: false,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                },
                yAxis: 1,
                name: 'pressure'
            }
        };
        
        this.windSpeedChart = new Highcharts.Chart({
            chart: {
                renderTo: this.body.down('.wind_speed', true),
                margin: [10, 65, 25, 40],
                zoomType: '',
                width: this.width,
                height: this.chartHeight
            },
            credits: {
                enabled: false
            },
            title: {
                text: null
            },
            legend: {
                enabled: false
            },
            xAxis: {
                type: 'datetime',
                tickInterval: 60 * 30 * 1000,
                name: ''
            },
            yAxis: {
                labels: {
                    formatter: function() {
                        return this.value.toFixed() + " kn";
                    }
                },
                title: { text: null},
                allowDecimals: false,
                tickInterval: 5,
                endOnTick: false,
                maxZoom: 15,
                startOnTick: true,
                lineWidth: 1
            },
            tooltip: {
                formatter: function() {
                    return Highcharts.dateFormat("%H:%M", this.x) + ": " + this.y.toFixed(1) + " kn";
                }
            },
            series: [
                this.chartSeries.gustSpeed,
                this.chartSeries.windSpeed
            ]
        });        
        this.chartSeries.windSpeed = this.windSpeedChart.get('sWindSpeed');     
        this.chartSeries.gustSpeed = this.windSpeedChart.get('sGustSpeed');     
        
        this.windDirectionChart = new Highcharts.Chart({
            chart: {
                renderTo: this.body.down('.wind_direction', true),
                margin: [10, 65, 25, 40],
                zoomType: '',
                width: this.width,
                height: this.chartHeight
            },
            credits: {
                enabled: false
            },
            title: {
                text: null
            },
            legend: {
                enabled: false
            },
            xAxis: {
                type: 'datetime',
                tickInterval: 60 * 30 * 1000,
                name: ''
            },
            yAxis: {
                labels: {
                    formatter: function() {
                        return this.value.toFixed() + "°";
                    }
                },
                title: { text: null},
                allowDecimals: false,
                minorTickInterval: 15,
                minorTickWidth: 1,
                minorGridLineWidth: 0,
                tickInterval: 45,
                tickWidth: 1,
                endOnTick: false,
                maxZoom: 100,
                startOnTick: false,
                lineWidth: 1
            },
            tooltip: {
                formatter: function() {
                    return Highcharts.dateFormat("%H:%M", this.x) + ": " + this.y.toFixed() + "°";
                }
            },
            series: [
                this.chartSeries.direction
            ]
        });
        this.chartSeries.direction = this.windDirectionChart.get('sDirection');     

        this.tempPressureChart = new Highcharts.Chart({
            chart: {
                renderTo: this.body.down('.temp_pressure', true),
                margin: [10, 65, 25, 40],
                zoomType: '',
                width: this.width,
                height: this.chartHeight
            },
            credits: {
                enabled: false
            },
            title: {
                text: null
            },
            legend: {
                enabled: false
            },
            xAxis: {
                type: 'datetime',
                tickInterval: 60 * 30 * 1000,
                name: ''
            },
            yAxis: [
                {
                    labels: {
                        formatter: function() {
                            return this.value.toFixed() + "°C";
                        }
                    },
                    title: {
                        text: null
                    },
                    tickInterval: 5,
                    maxZoom: 20,
                    lineWidth: 1
                },
                {
                    labels: {
                        formatter: function() {
                            return this.value.toFixed() + " hPa";
                        }
                    },
                    title: {
                        text: null
                    },
                    allowDecimals: false,
                    maxZoom: 50,
                    opposite: true,
                    lineWidth: 1
                }
            ],
            tooltip: {
                formatter: function() {
                    var m = Highcharts.dateFormat("%H:%M", this.x);
                    if (this.series.name == 'temp') {
                        m += ': ' + this.y.toFixed(1) + '°C';
                    } else if (this.series.name == 'pressure') {
                        m += ': ' + this.y.toFixed(1) + ' hPa';
                    }
                    return m
                }
            },
            series: [
                this.chartSeries.temp,
                this.chartSeries.pressure
            ]
        });
        this.chartSeries.temp = this.tempPressureChart.get('sTemp');     
        this.chartSeries.pressure = this.tempPressureChart.get('sPressure');     
    },
    setTitle : function(text) {
        this.dockedItems.get(0).setTitle(text);
    },
    setStation : function(id) {
        this.scroller.setOffset(new Ext.util.Offset(0,0), false);
        this.setTitle("Loading...");
        this.elLatest.setHTML('');
        this.elCredits.setHTML('');
        this.body.down('.history').hide();
        this.setLoading(true);
        this._loadStation(id);
    },
    _loadStation : function(id, cb) {
        this.stationId = id;
        Ext.Ajax.request({
            url: 'stations/' + id + '/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                
                this.updateData(data);
                this.setLoading(false);
                cb && cb();
            },
            failure: function(response, opts) {
                console.log('loading station', id, ': got status:', response.status);
                this.elLatest.setHTML('Error loading data.');
                this.setLoading(false);
                cb && cb();
            }
        });
    },
    updateData : function(data) {
        this.setTitle(data.name);
        if (data.source_credit) {
            this.elCredits.setHTML('Source: ' + data.source_credit);
        }
        
        if (data.latest) {
            data.latest.time = new Date(data.latest.time);
            data.latest.wind_speed = data.latest.wind_speed.toFixed(1);
            data.latest.gust_speed = data.latest.gust_speed.toFixed(1);
            data.latest.wind_compass = this._compass_sector(data.latest.wind_direction);
            this.tpl_latest.overwrite(this.elLatest, data.latest);
        } else {
            this.elLatest.setHTML("<p class='obTime'>No recent observation available</p>")
        }
        
        if (data.history) {
            var h = data.history;
            this.body.down('.history').show();

            Ext.get(this.windSpeedChart.container).setVisible(h.wind_speed.length || h.gust_speed.length);
            Ext.get(this.windDirectionChart.container).setVisible(h.wind_direction.length);
            Ext.get(this.tempPressureChart.container).setVisible(h.temp.length || h.pressure.length);
            
            this.chartSeries.windSpeed.setData(h.wind_speed);
            this.chartSeries.gustSpeed.setData(h.gust_speed);
            this.chartSeries.direction.setData(h.wind_direction);
            this.chartSeries.temp.setData(h.temp);
            this.chartSeries.pressure.setData(h.pressure);

        }
    },
    _COMPASS_POINTS : [
        'N','NNE','NE','ENE',
        'E','ESE','SE','SSE',
        'S','SSW','SW','WSW',
        'W','WNW','NW','NNW',
        'N'
    ],
    _compass_sector : function(direction) {
        var s = Math.round((direction % 360) / 22.5);
        return this._COMPASS_POINTS[s];
    }
});

Ext.reg('YStation', Y.views.Station);
