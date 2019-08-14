var headertext = [],
    headers = document.querySelectorAll(".responce-table th"),
    tablerows = document.querySelectorAll(".responce-table th"),
    tablebody = document.querySelector(".responce-table tbody");

for (var i = 0; i < headers.length; i++) {
    var current = headers[i];
    headertext.push(current.textContent.replace(/\r?\n|\r/, ""));
}
for (var i = 0, row; row = tablebody.rows[i]; i++) {
    for (var j = 0, col; col = row.cells[j]; j++) {
        col.setAttribute("data-th", headertext[j]);
    }
}

function idvalue(){
  var elem = event.target;
  var url = "/";
  url = elem.parentElement.cells[0].textContent;
  $(location).attr('href',url);
}

/*$("tr").hover(function () {
    $('tr').toggleClass("table-info");
 });*/
