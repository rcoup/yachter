Y.views.TideChart = Ext.extend(Ext.Panel, {
    title: "Tides",
    iconCls: 'info',
    baseCls: 'y-tidechart',
    monitorResize: true,
    chart: null,
    monitorOrientation: true,

    initComponent : function() {
        Y.views.TideChart.superclass.initComponent.call(this);

        this.curveSeries = {
            id: 'sCurve',
            type: 'spline',
            color: '#0000ff',
            marker: {
                enabled: false,
                states: {
                    hover: {
                        enabled: true
                    }
                }
            }  
        };
        this.nowSeries = {
            id: 'sNow',
            type: 'scatter',
            pointWidth: 3,
            color: '#ff0000',
            dataLabels: {
                enabled: true,
                formatter: function() {
                    return this.y.toFixed(1) + "m ";
                }                
            }
        };
        this.tideSeries = {
            id: 'sTides',
            type: 'scatter',
            pointWidth: 3,
            color: '#0000ff',
            dataLabels: {
                enabled: true,
                formatter: function() {
                    return Highcharts.dateFormat("%H:%M", this.x);
                }                
            }
        };
        
        Ext.Ajax.request({
            url: 'tides/heights/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                
                if (this.chart) {
                    this.curveSeries.options.pointStart = data.heights.pointStart;
                    this.curveSeries.options.pointInterval = data.heights.pointInterval;
                    this.curveSeries.setData(data.heights.data);
                                  
                    this.tideSeries.setData(data.tides.data);
                    this.nowSeries.setData(data.now.data);
                } else {
                    Ext.apply(this.curveSeries, data.heights);
                    Ext.apply(this.tideSeries, data.tides);
                    Ext.apply(this.nowSeries, data.now);
                }
            }
        });
        
        this.addManagedListener(this, 'resize', this.onResize, this);
        this.addManagedListener(this, 'orientationchange', this.onResize, this);
        this.addManagedListener(this, 'show', function() {
            this.onResize(this.getWidth(), this.getHeight());
        }, this);
    },
            
    onResize: function(w, h) {
        if (this.chart) {
            this.chart.xAxis[0].options.tickInterval = ((w < 400) ? 2 : 1) * 3600 * 1000;
            this.isVisible() && this.chart.setSize(w, h, false);
        }
    },
    
    afterRender : function() {
        Y.views.TideChart.superclass.afterRender.apply(this, arguments);

        this.chart = new Highcharts.Chart({
            chart: {
                renderTo: this.body.dom,
                margin: [10, 20, 25, 45],
                zoomType: '',
                width: this.getWidth(),
                height: this.getHeight() || this.container.getHeight()
            },
            credits: {
                enabled: false
            },
            title: {
                text: ''
            },
            legend: {
                enabled: false
            },
            xAxis: {
                type: 'datetime',
                tickInterval: 3600 * 1000,
                name: ''
            },
            yAxis: {
                labels: {
                    formatter: function() {
                        return this.value.toFixed(1) + " m";
                    }
                },
                name: ''
            },
            tooltip: {
                formatter: function() {
                    return Highcharts.dateFormat("%H:%M", this.x) + ": " + this.y.toFixed(1) + " m ";
                }
            },
            series: [
                this.curveSeries,
                this.tideSeries,
                this.nowSeries
            ]
        });        
        
        this.curveSeries = this.chart.get('sCurve');
        this.nowSeries = this.chart.get('sNow');
        this.tideSeries = this.chart.get('sTides');
    }
});

Ext.reg('YTideChart', Y.views.TideChart);
