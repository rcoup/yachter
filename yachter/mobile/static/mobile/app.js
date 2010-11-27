/**
 * This file sets application-wide settings and launches the application when everything has
 * been loaded onto the page.
 * 
 * The global variable Y holds a reference to the application, and namespaces are automatically
 * set up for Y.views, Y.models, Y.controllers and Y.stores
 */ 
Ext.regApplication({
    name: "Y",

    tabletStartupScreen: '/static/mobile/images/tablet_startup.png',
    phoneStartupScreen: '/static/mobile/images/phone_startup.png',
    fullscreen: true,
    icon: '/static/mobile/images/icon.png',
    glossOnIcon: false,
    statusBarStyle: 'black',
    
    /**
     * This function is automatically called when the document has finished loading. All we do here
     * is launch the application by calling the main controller's 'map' action (see app/controllers/main.js)
     */
    launch: function() {
        Ext.dispatch({
            controller: 'main',
            action    : 'initial'
        });
    }
});
