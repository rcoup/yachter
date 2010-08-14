var map;

$(function() {
    map = new OpenLayers.Map('map', {
        units: "m",
        maxResolution: 156543.0339,
        numZoomLevels: 20,
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        wrapDateLine: true
    });

    map.addLayer(new OpenLayers.Layer.OSM(null, null, {
        displayOutsideMaxExtent: true,
        wrapDateLine: true,
        transitionEffect: 'resize',
        attribution: "Map &copy; <a href='http://www.openstreetmap.org'>OpenStreetMap</a>."
    }));
    
    var pWKT = new OpenLayers.Format.WKT();
    
    var lCourse = new OpenLayers.Layer.Vector("Selected Course", {
        styleMap : new OpenLayers.StyleMap({
            'default': {
                strokeColor: '#FF4500',
                strokeWidth: 3,
                strokeOpacity: 0.8
            }
        })
    });
    map.addLayer(lCourse);
    
    var lMarks;
    $.getJSON('data/marks.json', function(mark_data) {
        lMarks = new OpenLayers.Layer.Vector("Marks", {
            styleMap: new OpenLayers.StyleMap({
                'default': {
                    strokeColor: "#FFD700",
                    strokeOpacity: 1,
                    strokeWidth: 1,
                    fillColor: "#FFFF00",
                    fillOpacity: '0.8',
                    pointRadius: 5
                },
                'select': {
                    fillOpacity: 1.0,
                    strokeWidth: 2,
                    label : "${name}",
                    labelAlign: 'lb',
                    fontColor: "#000000",
                    fontSize: "11px",
                    fontFamily: "Verdana, Arial, sans-serif"
                }
            })
        });  
        var fMarks = [];
        $.each(mark_data, function(i, mark) {
            var f = pWKT.read(mark.location_globalMercator);
            f.attributes['name'] = mark.name;
            f.attributes['id'] = mark.id;
            mark.feature = f;
            fMarks.push(f);
        });
        lMarks.addFeatures(fMarks);
        map.addLayer(lMarks);
        map.zoomToExtent(lMarks.getDataExtent());
        
        var cSelect = new OpenLayers.Control.SelectFeature(lMarks, {hover: true});
        map.addControl(cSelect);
        cSelect.activate();
    });
    
    // Make our course-selector work
    var currentCourseId = -1;
    var courseFeature;
    var nC = $('#course_info');
    $('#course_select').change(function(e) {
        var cId = parseInt(this.value);
        if (cId < 0 || cId != currentCourseId) {
            // remove any old stuff
            $('#course_info > *').remove();
            if (courseFeature) {
                lCourse.removeFeatures([courseFeature]);
            }
            if (cId > 0) {
                $.getJSON('data/course_' + cId + '.json', function(c) {
                    $("<h2/>").text('Course ' + c.number).appendTo(nC);
                    var nInfo = $("<ul/>").appendTo(nC);
                    $("<li/>").text('Length: ' + c.length.toFixed(1) + ' Nm').appendTo(nInfo);
                    $("<li/>").text('Can Shorten? ' + (c.can_shorten ? 'Yes' : 'No')).appendTo(nInfo);
                    if (c.can_shorten) {
                        $("<li/>").text('Shortened Length ' + c.shortened_length.toFixed(1) + ' Nm').appendTo(nInfo);
                    }

                    $.each(c.marks, function(i, cm) {
                        $("<h3/>").text((i+1) + ': ' + cm.mark.name + ' (' + cm.rounding_display + ')').appendTo(nC);
                    });
                    
                    if (window.renderCourseExtra) {
                        window.renderCourseExtra(c, nC);
                    }
                    
                    // draw it
                    if (c.path_globalMercator) {
                        courseFeature = pWKT.read(c.path_globalMercator);
                        lCourse.addFeatures(courseFeature);
                        bounds = lCourse.getDataExtent();
                        map.zoomToExtent(bounds);
                    } else if (lMarks.getDataExtent()) {
                        map.zoomToExtent(lMarks.getDataExtent());
                    }
                });
            } else if (lMarks.getDataExtent()) {
                map.zoomToExtent(lMarks.getDataExtent());
            }
        }
        currentCourseId = cId;
    }).trigger('change');
});
