Ext.regModel('Tide', {
    idProperty: 'id',
    fields: [
        {name:'time', type:'date'}, 
        {name:'height', type:'float'}, 
        {name:'type', type:'string'},
        {name:'id', type:'string'},
    ]
});
