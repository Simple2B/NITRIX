// custom javascript
$(document).ready(function() {
    function update_end_date() {
        let endDate = new Date($('#activation_date').val());
        let month = +$('#months').val();
        endDate.setMonth(endDate.getMonth() + month);
        $("#endDate")[0].valueAsDate = endDate;
    };
    $('#activation_date').change(update_end_date);
    $('#months').change(update_end_date);
    update_end_date();
} );