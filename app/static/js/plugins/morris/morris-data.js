$(function() {
    $(".morris-area-chart-temperature").each(function(){
        var location_id = $(this).data('location_id');
        var graph = this;
        $.getJSON($SCRIPT_ROOT + '/weather/_graph/get_temperature/' + location_id,
        {},
        function(data) {
            if (!data.data.length){
                $(graph).text('No data collected yet.');
            } else {
                Morris.Line(data);
            }
        });
    });
    $(".morris-area-chart-wind").each(function(){
        var location_id = $(this).data('location_id');
        var graph = this;
        $.getJSON($SCRIPT_ROOT + '/weather/_graph/get_wind/' + location_id,
        {},
        function(data) {
            if (!data.data.length){
                $(graph).text('No data collected yet.');
            } else {
                Morris.Area(data);
            }
        });
    });
});
