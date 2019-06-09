$(document).ready(function() {
    var table = $('#overview').DataTable({
        "columnDefs": [
            {
                "targets": [-1],
                "class": "convRate"
            },
            {
                "targets": [2],
                "class": "avgPos"
            },
            {
                "targets": [0],
                "visible": true
            },
        ],
        buttons: [
            {
                extend: 'excel',
                text: 'expert to csv'
            },
            {
                extend: 'pdf',
                text: 'expert to pdf'
            }
        ]
    });

    function maxValue(table, colSelector) {
        var highValue = 0
        var valArray = table.column(colSelector)
                               .data()

        for (var i=0;i<valArray.length;i++) {
            if (!isNaN(valArray[i])) {
                currentValue = parseFloat(valArray[i])
                if (currentValue > highValue)
                    highValue = currentValue
            }
        }
        return highValue;
    }

    function avgConvRate(table, colSelector) {
        var valArray = table.column(colSelector)
                               .data()
        const len = valArray.length

        if (len < 1)
            return 0
        var sum = 0.0

        for (var i=0;i<len;i++) {
            sum = sum + parseFloat(valArray[i])
        }
        return sum/len;
    }

    var maxPos = maxValue(table, '.avgPos')
    var AB = avgConvRate(table, '.convRate')

    $.fn.dataTable.ext.type.order['weighted-pre'] = function (a) {
        const index = parseInt(a)
        return index
        var pos = parseFloat(table.column('.avgPos').data()[index - 1])
        var rate = parseFloat(table.column('.convRate').data()[index - 1])
        etv = (pos / maxPos) * rate + (1 - (pos / maxPos)) * AB
        return etv
    }
    
    function weighted(a) {
        const index = parseInt(a)
        var pos = parseFloat(table.column('.avgPos').data()[index - 1])
        var rate = parseFloat(table.column('.convRate').data()[index - 1])
        etv = (pos / maxPos) * rate + (1 - (pos / maxPos)) * AB
        return etv
    }

    $.fn.dataTable.ext.search.push(
        function( settings, data, dataIndex ) {
            var p_st = $('#pos_st').val(), p_ed = $('#pos_ed').val();
            var c_st = $('#con_st').val(), c_ed = $('#con_ed').val();

            var position = parseFloat( data[2] ) || 0.0; // use data for the position column
            var conv_rate = parseFloat( data[6]) || 0.0; // use data for the conversion rate

            let b_pos = false

            if ( ( ( p_st == '' ) && (p_ed == '' ) ) ||
                ( ( p_st == '' ) && position <= p_ed ) ||
                ( p_st <= position   && (p_ed == '' ) ) ||
                ( p_st <= position   && position <= p_ed ) )
            {
                b_pos = true
            }

            let b_con = false
            if ( ( ( c_st == '' ) && (c_ed == '') ) ||
            ( c_st == '' && conv_rate <= c_ed ) ||
            ( c_st <= conv_rate   && ( c_ed == '' ) ) ||
            ( c_st <= conv_rate   && conv_rate <= c_ed ) )
            {
                b_con = true
            }
            return b_con && b_pos
        }
    );

} );

$(function() {

    var start = moment().subtract(365, 'days');
    var end = moment();

    function cb(start, end) {
        $('#reportrange').val(start.format('MM/DD/YYYY') + ' - ' + end.format('MM/DD/YYYY'));
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