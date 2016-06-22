$(document).ready(function() {
    chart = new Highcharts.Chart({
        chart: {
            renderTo: 'chart',
            defaultSeriesType: 'spline',
            events: {
                load: requestData
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

        title: {
            text: 'Live charting'
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150,
            maxZoom: 20 * 1000
        },
        yAxis: {
            minPadding: 0.2,
            maxPadding: 0.2,
            title: {
                text: 'Value',
                margin: 80
            }
        },
        series: [{
            name: 'Data',
            data: []
        }]
    });
});


function requestData() {
    $.ajax({
        url: '/random_data',
        success: function(point) {
            var series = chart.series[0],
                shift = series.data.length > 1000; // shift if the series is
            // add the point
            var x = (new Date()).getTime();
            var y = point;
            chart.series[0].addPoint([x,y], true, shift);
            setTimeout(requestData, 1);
        },
        cache: true
    });
}

