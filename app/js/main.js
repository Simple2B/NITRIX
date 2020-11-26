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

$(document).ready(function() {
    $('#theTable').DataTable({
        "info" : false,
        "paging" : false,
        "pageLength": linesPerPage,
        "order": [],
        "displayStart": (page ? page : 0)
    });
} );