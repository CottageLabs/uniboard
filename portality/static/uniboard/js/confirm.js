jQuery(document).ready(function(event){

  $(".delete_advert").click(function(){
    var c = confirm("Are you sure you wish to deactivate this advert?")
    if (!c) {
        return false;
     }
  });

    $(".activate_advert").click(function() {
        var c = confirm("Are you sure you wish to re-activate this advert?")
        if (!c) {
            return false;
         }
    });

});