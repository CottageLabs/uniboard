
jQuery(document).ready(function($) {
    //$('#m').hide()
    $('#m').css({
        "border":"none",
        "background":"none",
        "cursor":"default",
        "-moz-box-shadow":"none",
        "-webkit-box-shadow":"none",
        "box-shadow":"none"
    })
    /*
    var signup = function(event) {
        event.preventDefault()
        if ( $('#m').val() == "" ) {
            $('#signupform').submit()
        } else {
            alert("Are you human? If so, don't put anything in that last box...")
        }
    }
    */

    function autocomplete(selector, doc_field, doc_type) {
        $(selector).select2({
            minimumInputLength: 3,
            ajax: {
                url: current_scheme + "//" + current_domain + "/autocomplete/" + doc_type + "/" + doc_field,
                dataType: 'json',
                data: function (term, page) {
                    return {
                        q: term
                    };
                },
                results: function (data, page) {
                    return { results: data["suggestions"] };
                }
            },
            createSearchChoice: function(term) {return {"id":term, "text": term};},
            initSelection : function (element, callback) {
                var data = {id: element.val(), text: element.val()};
                callback(data);
            }
        });
    }

    autocomplete('#degree', 'degree', 'account')

    $('#signup').bind('click',signup)
});