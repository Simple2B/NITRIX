// custom javascript
$(document).ready(function() {
    function update_end_date() {
        let endDate = new Date($('#activation_date').val());
        endDate.setHours(12,0,0,0);
        let month = +$('#months').val();
        endDate.setMonth(endDate.getMonth() + month);
        $("#endDate")[0].valueAsDate = endDate;
    };

    $('#activation_date').change(update_end_date);
    $('#months').change(update_end_date);
    update_end_date();

    document.querySelectorAll('.save_ext').forEach(row => {
        function update_end_date_ext() {
            let endDate = new Date(row.querySelector('.extension_datesave').value);
            let month = +row.querySelector('.monthssave').value;
            endDate.setMonth(endDate.getMonth() + month);
            row.querySelector('.enddatesave').valueAsDate = endDate;
        };
        row.querySelector('.extension_datesave').addEventListener('change', update_end_date_ext);
        row.querySelector('.monthssave').addEventListener('change', update_end_date_ext);
        update_end_date_ext();
    });


} );

