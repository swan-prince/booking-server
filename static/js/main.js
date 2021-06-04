$(document).ready(function(){
    // nav link active script
    $('.dropdown-menu a.active').closest(".position-relative").find("a.nav-link:first").addClass("active");
 });
