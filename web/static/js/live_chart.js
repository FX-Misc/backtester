$(document).ready(function() {
    console.log( "account info ready!" );
    chart();
});

function chart() {

    Highcharts.setOptions({
        global : {
            useUTC : false
        }
    });

    // Create the chart
    $('#chart').highcharts('StockChart', {
        chart : {
            events : {
                load : function () {
                    // set up the updating of the chart each second
                    var series = this.series[0];
                    setInterval(function () {
                   var x, y;
                    $.ajax({
                        url: '/random_data',
                        success: function(point){
                            console.log(point);
                            x = (new Date()).getTime(), // current time
                            //y = Math.round(Math.random() * 100);
                                y = point;
                            //setTimeout(requestAccountInfo, 100);
                            series.addPoint([x, y], true, true);
                            console.log(x, y);
                        },
                        cache: false
                    });
                    }, 1);
                }
            }
        },

        rangeSelector: {
            buttons: [{
                count: 1,
                type: 'minute',
                text: '1M'
            }, {
                count: 5,
                type: 'minute',
                text: '5M'
            }, {
                type: 'all',
                text: 'All'
            }],
            inputEnabled: false,
            selected: 0
        },

        title : {
            text : 'Live charting'
        },

        exporting: {
            enabled: false
        },

        series : [{
            name : 'Random data',
            data : (function () {
                // generate an array of random data
                var data = [], time = (new Date()).getTime(), i;

                for (i = -999; i <= 0; i += 1) {
                    data.push([
                        time + i * 1000,
                        Math.round(Math.random() * 100)
                    ]);
                }
                return data;
            }())
        }]
    });

}
