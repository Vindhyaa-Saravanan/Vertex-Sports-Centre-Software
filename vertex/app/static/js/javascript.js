/* static/javascript.js */

/* Function for manager to search tables using name or entry id */
function myTableSearchFunction() {
    var input, filter, table, tr, td1, td2, i, txtValue1, txtValue2;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {

        /* Search by both name and id*/
        td1 = tr[i].getElementsByTagName("td")[0]; // First td element in each tr
        td2 = tr[i].getElementsByTagName("td")[1]; // Second td element in each tr
        if (td1 && td2) {
            txtValue1 = td1.textContent || td1.innerText; // Get text content from td1
            txtValue2 = td2.textContent || td2.innerText; // Get text content from td2
            if (txtValue1.toUpperCase().indexOf(filter) > -1 || txtValue2.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

/* Function for manager to search tables using name or entry id */
function myTableSearchFunction1() {
    var input, filter, table, tr, td1, td2, i, txtValue1, txtValue2;
    input = document.getElementById("myInput1");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable1");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {

        /* Search by both name and id*/
        td1 = tr[i].getElementsByTagName("td")[0]; // First td element in each tr
        td2 = tr[i].getElementsByTagName("td")[1]; // Second td element in each tr
        if (td1 && td2) {
            txtValue1 = td1.textContent || td1.innerText; // Get text content from td1
            txtValue2 = td2.textContent || td2.innerText; // Get text content from td2
            if (txtValue1.toUpperCase().indexOf(filter) > -1 || txtValue2.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

/* FOR GOOGLE TRANSLATE LANGUAGE SELECTION */
document.querySelectorAll('.language-link').forEach(function(link) {
    link.addEventListener('click', function(event) {
      event.preventDefault();
      var lang = this.getAttribute('data-lang');
      /* Switch to the selected language */
    });
  });
  