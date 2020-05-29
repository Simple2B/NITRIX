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

    function update_end_date_ext() {
        let endDate = new Date($('#extension_date').val());
        let month = +$('#monthsExt').val();
        endDate.setMonth(endDate.getMonth() + month);
        $("#endDateExt")[0].valueAsDate = endDate;
    };

    $('#extension_date').change(update_end_date_ext);
    $('#monthsExt').change(update_end_date_ext);
    update_end_date_ext();

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



    // function update_end_date_ext_save() {
    //     let endDate = new Date($('.form-control extension_datesave').val());
    //     let month = +$('.form-control monthssave').val();
    //     endDate.setMonth(endDate.getMonth() + month);
    //     $(".form-control enddatesave")[0].valueAsDate = endDate;
    // };

    // $('.form-control extension_datesave').change(update_end_date_ext_save);
    // $('.form-control monthssave').change(update_end_date_ext_save);
    // update_end_date_ext_save();
} );

