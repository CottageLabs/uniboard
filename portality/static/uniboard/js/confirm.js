jQuery(document).ready(function(event){

  $(".deactivate_advert").click(function(){
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

  $(".delete_advert").click(function(){
    var c = confirm("Are you sure you wish to delete this advert?")
    if (!c) {
        return false;
     }
  });

    $(".undelete_advert").click(function() {
        var c = confirm("Are you sure you wish to undelete this advert?")
        if (!c) {
            return false;
         }
    });

    $("#delete_account").click(function() {
        var c = confirm("Are you sure you wish to delete your account?")
        if (!c) {
            return false;
         }
    });

});