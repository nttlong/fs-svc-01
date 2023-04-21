$("#tabulator").tabulator({
     dataLoaded:function(data){ //freeze first row on data load
        var firstRow = $("#tabulator-frozen-row").tabulator("getRows")[0];

        if(firstRow){
            firstRow.freeze();
        }
     }
 });