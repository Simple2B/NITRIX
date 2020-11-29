// custom javascript

const linesPerPage = 50
const params = new URLSearchParams(window.location.search)
let id = parseInt(params.get('id'))
if (id.isNan){
    var page = 0
}
else{
    var page = (parseInt((id - 1) / linesPerPage) * linesPerPage)
}
$(document).ready(function(){
$(function(){
    let execute =false
    if(!execute)
    execute=true
    let x = document.getElementById("rows_per_page").getAttribute('data-row');
    $("#rows_per_page").val(x);
});

$("#rows_per_page").change(function(){
    let rows_per_page = $(this).val()
    const rows_param = "rows_per_page";
    const queryString = window.location.search
    const urlParams = new URLSearchParams(queryString);
    if(!urlParams.has(rows_param)){
        urlParams.append(rows_param, rows_per_page)
    }
    else if(urlParams.get(rows_param)==rows_per_page){
        return
    }
    else{
        urlParams.set(rows_param, rows_per_page)
    }
    window.open(`accounts?${urlParams}`,'_self')

})

    $('#theTable').DataTable({
        // "searching":false,
        // "info" : false,
        // "paging" : false,
        "pageLength": linesPerPage,
        "order": [],
        "displayStart": (page ? page : 0)
    });



    $('#theAccountTable').DataTable({
        "searching":false,
        "info" : false,
        "paging" : false,
        "pageLength": linesPerPage,
        "order": [],
        "displayStart": (page ? page : 0)
    });
}) 