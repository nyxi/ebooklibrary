function titleGo() {
    var list=document.getElementById("titleList");
    window.location.assign("https://www.goodreads.com/book/show/" + list.options[list.selectedIndex].value)
}
function authorGo() {
    var list=document.getElementById("authorList");
    window.location.assign("/author/" + list.options[list.selectedIndex].value)
}
