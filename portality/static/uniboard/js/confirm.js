jQuery(document).ready(function(event){
  $("#delete").click(function(){
    var c = confirm("Are you sure you wish to delete this advert?")
    if (!c) {
        return false;
     }
  });
});