Y.views.Forecast = Ext.extend(Ext.Component, {
    title: "Forecast",
    baseCls: "y-forecast",
    iconCls: "info",
    scroll: "vertical",

    tpl: new Ext.XTemplate(
        '<tpl for=".">',
            '<dl>',
                '<dt>Issued at:</dt> <dd>{issued}</dd>',
                '<dt>Warning:</dt> <dd>{warning}</dd>',
                /*
                '<dt>Situation:</dt> <dd>{situation}</dd>',
                */
                '<dt>Forecast:</dt> <dd>{forecast_html}</dd>',
                '<dt><span style="display:none">Outlook:</span></dt> <dd>{outlook_html}</dd>',
                '<dt><span style="display:none">Swell:</span></dt> <dd>{swell_html}</dd>',
                /*
                '<dt><span style="display:none">Tides:</span></dt> <dd>',
                    '<tpl for="tides">',
                        '<strong>High Tides at {location}:</strong>',
                        '<ul>',
                            '<tpl for="tides">',
                                '<li>{time} - {height} m</li>',
                            '</tpl>',
                        '</ul>',
                    '</tpl>',
                '</dd>',
                */
                '<dt>Valid to:</dt> <dd>{validTo}</dd>',
            '</dl>',
            '<p class="credits">Source: MetService</p>',
        '</tpl>'
    ),

    plugins: [new Ext.ux.touch.ListPullRefresh({
        reloadFn: function(cb, scope) {
            scope.cmp._loadForecast(Ext.createDelegate(cb, this));
        }
    })],
    
    initComponent : function() {
        Y.views.Forecast.superclass.initComponent.call(this);
    },
    
    afterRender : function() {
        Y.views.Forecast.superclass.afterRender.apply(this, arguments);
        this._loadForecast();
    },
    
    _loadForecast : function(cb) {
        this.setLoading(true);
    
        Ext.Ajax.request({
            url: 'forecast/',
            scope: this,
            success: function(response, opts) {
                var data = Ext.decode(response.responseText);
                
                // fiddle some data
                Ext.each(['forecast', 'swell', 'outlook'], function(k) {
                    var s = data[k];
                    var rs = "";
                    var parts = s.split(':');
                    Ext.each(parts, function(p, j) {
                        var tp = Ext.util.Format.trim(p);
                        var i = tp.lastIndexOf('.');
                        var before = Ext.util.Format.trim(tp.substring(0, i+1)); 
                        var after = Ext.util.Format.trim(tp.substring(i+1));
                        if (before) {
                            rs += before;
                        }
                        if (after) {
                            if (j) {
                                rs += "<br/>";
                            }
                            rs += "<strong>" + after + ":</strong> ";
                        }
                    });
                    data[k + "_html"] = rs;
                });
                
                this.update(data);
                this.setLoading(false);
                cb && cb();
            },
            failure: function(response, opts) {
                console.error('loading forecast: got status:', response.status);
                this.setLoading(false);
                cb && cb();
            }
        });
    }
});

Ext.reg('YForecast', Y.views.Forecast);
