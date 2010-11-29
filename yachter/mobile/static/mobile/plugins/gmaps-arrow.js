/*
Derived from:
http://www.bdcc.co.uk/Gmaps/BDCCArrow.js
http://www.bdcc.co.uk/Gmaps/BdccGmapBits.htm
Bill Chadwick 2007
*/

function WindArrow(options) {
    this._svgId = "WindArrow" + (WindArrow._counter++);

    this._position = options.position;
    this._rotation = options.rotation || 0;
    this._scale = options.scale || 1.0;

    var r = this._rotation + 90;//compass to math
    this._dx = (20*this._scale)*Math.cos(r*Math.PI/180);//other end of arrow line to point
    this._dy = (20*this._scale)*Math.sin(r*Math.PI/180);

    this._color = options.color || "#888888";
    this._opacity = options.opacity || 0.5;
    this._title = options.title;

    options.map && this.setMap(options.map);
}
WindArrow.prototype = new google.maps.OverlayView();
WindArrow._counter = 0;


WindArrow.prototype.getPosition = function(){
    return this._position;
}

WindArrow.prototype.getTitle = function(){
    return this._title;
}

WindArrow.prototype.clicked = function(e) {
    google.maps.event.trigger(this, "click", this, e);
}

// Creates the DIV representing this arrow.
WindArrow.prototype.onAdd = function() {
    this._div = document.createElement("div");
    this._div.title = this._title;
    this._div.style.zIndex = 10;

    // make a 40x40 pixel space centered on the arrow 
    var svgNS = "http://www.w3.org/2000/svg";
    var svgRoot = document.createElementNS(svgNS, "svg");
    svgRoot.setAttribute("cursor", "pointer");
    svgRoot.setAttribute("width", (40*this._scale));
    svgRoot.setAttribute("height", (40*this._scale));
    svgRoot.setAttribute("stroke", this._color);
    svgRoot.setAttribute("fill", this._color);
    svgRoot.setAttribute("stroke-opacity", this._opacity);
    svgRoot.setAttribute("fill-opacity", this._opacity);
    this._div.appendChild(svgRoot);
    
    var svgRect = document.createElementNS(svgNS, "rect");
    svgRect.setAttribute("fill-opacity", 0.01);
    svgRect.setAttribute("fill", "white");
    svgRect.setAttribute("stroke-width", 0);
    svgRect.setAttribute("x", 0);
    svgRect.setAttribute("y", 0);
    svgRect.setAttribute("width", '100%');
    svgRect.setAttribute("height", '100%');
    svgRoot.appendChild(svgRect);

    var svgNode = document.createElementNS(svgNS, "line");
    svgNode.setAttribute("stroke-width", 3);
    svgNode.setAttribute("x1", (20*this._scale)+(-0.5 * this._dx));
    svgNode.setAttribute("y1", (20*this._scale)+(-0.5 * this._dy));
    svgNode.setAttribute("x2", (20*this._scale)+(0.5 * this._dx));
    svgNode.setAttribute("y2", (20*this._scale)+(0.5 * this._dy));
    this._svgNode = svgNode;

    //make a solid arrow head, can't share these, as in SVG1.1 they can't get color from the referencing object, only their parent
    //a bit more involved than the VML
    var svgM = document.createElementNS(svgNS, "marker");
    svgM.id=this._svgId;
    svgM.setAttribute("viewBox","0 0 10 10");
    svgM.setAttribute("refX",0);
    svgM.setAttribute("refY",5); 
    svgM.setAttribute("markerWidth",4);
    svgM.setAttribute("markerHeight",3);
    svgM.setAttribute("orient","auto");
    var svgPath = document.createElementNS(svgNS, "path");//could share this with 'def' and 'use' but hardly worth it 
    svgPath.setAttribute("d","M 10 0 L 0 5 L 10 10 z");
    svgM.appendChild(svgPath);
    svgRoot.appendChild(svgM);
    svgNode.setAttribute("marker-start","url(#" + this._svgId + ")");
    this._svgM = svgM;

    svgRoot.appendChild(svgNode);
    this._svgRoot = svgRoot;

    // Arrow is similar to a marker, so add to plane just below marker pane
    var panes = this.getPanes();
    panes.overlayMouseTarget.appendChild(this._div);

    //Ext.EventManager.on(svgRoot, 'click', this.clicked, this);
    Ext.EventManager.on(svgRoot, 'click', this.clicked, this);
}

// Remove the main DIV from the map pane
WindArrow.prototype.onRemove = function() {
    google.maps.removeListener(this._hClick);
    google.maps.removeListener(this._hTap);
    this._div.parentNode.removeChild(this._div);
    delete this._hClick;
    delete this._svgRoot;
    delete this._svgNode;
    delete this._svgM;
    delete this._div;
}

// Redraw the arrow based on the current projection and zoom level
WindArrow.prototype.draw = function() {
    // Calculate the DIV coordinates of the ref point of our arrow
    var overlayProjection = this.getProjection();
    var p = overlayProjection.fromLatLngToDivPixel(this._position);
    
    var x2 = p.x + this._dx; 
    var y2 = p.y + this._dy; 

    this._svgRoot.setAttribute("style", "position:absolute; top:"+ (p.y-(20*this._scale)) + "px; left:" + (p.x-(20*this._scale)) + "px");
}
