window.Y = window.Y || {};

Y.TideChartPanel = Ext.extend(Ext.Panel, {
    title: "Tides",
    cls: 'tides',
    scroll: 'vertical',
    iconCls: 'info',
    monitorResize: true,
    chart: null,

    initComponent : function() {
        Y.TideChartPanel.superclass.initComponent.call(this);

        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
        
        this.curveSeries = {
            id: 'sCurve',
            type: 'spline',
            color: '#0000ff',
            marker: {
                'enabled': false
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
        
        this.addManagedListener(this, 'resize', function(w, h) {
                console.log('onResize', w, h);
                this.chart && this.chart.setSize(w, h);
            }, this);

        this.addManagedListener(this, 'show', function() {
                var w = this.getWidth();
                var h = this.getHeight();
                console.log('onShow', w, h);
                this.chart && this.chart.setSize(w, h);
            }, this);

    },
            
    afterRender : function() {
        Y.TideChartPanel.superclass.afterRender.apply(this, arguments);

        this.chart = new Highcharts.Chart({
            chart: {
                renderTo: this.el.dom,
                margin: [10, 20, 25, 45],
                zoomType: 'xy',
                width: this.getWidth(),
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
