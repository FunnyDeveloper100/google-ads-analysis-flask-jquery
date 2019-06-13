
$(function() {

    var start = moment().subtract(365, 'days');
    var end = moment();

    function cb(start, end) {
        //$('#daterange').val(start.format('MM/DD/YYYY') + ' - ' + end.format('MM/DD/YYYY'));
    }

    $('#reportrange').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
           'Last 7 Days': [moment().subtract(7, 'days'), moment()],
           'Last 28 Days': [moment().subtract(28, 'days'), moment()],
           'Last 3 Months': [moment().subtract(3, 'month'), moment()],
           'Last 6 Months': [moment().subtract(6, 'month'), moment()],
           'Last 9 Months': [moment().subtract(9, 'month'), moment()],
           'Last 12 Months': [moment().subtract(12, 'month'), moment()],
           'Last 16 Months': [moment().subtract(16, 'month'), moment()],
        }
    }, cb);
    cb(start, end);
});