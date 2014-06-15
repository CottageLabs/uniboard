jQuery(document).ready(function($) {
        $('#condition').select2({
            allowClear: true
        });

        $('#location').select2({
            allowClear: true
        });
    });

$('#postcode-container').hide();

$('#location').change(function(e){
  if ($('#location').val() == 'postcode'){
    $('#postcode-container').show();
  }else{
    $('#postcode-container').hide();
  }
});

(function () {
    var takePicture = document.querySelector("#take-picture"),
        showPicture = document.querySelector("#show-picture");

    $('#preview').hide();

    if (takePicture && showPicture) {
        // Set events
        takePicture.onchange = function (event) {
            // Get a reference to the taken picture or chosen file
            var files = event.target.files,
                file;
            if (files && files.length > 0) {
                file = files[0];
                try {
                    // Get window.URL object
                    var URL = window.URL || window.webkitURL;

                    // Create ObjectURL
                    var imgURL = URL.createObjectURL(file);

                    // Set img src to ObjectURL
                    showPicture.src = imgURL;
                    $('#preview').show();

                    // Revoke ObjectURL
                    URL.revokeObjectURL(imgURL);
                }
                catch (e) {
                    try {
                        // Fallback if createObjectURL is not supported
                        var fileReader = new FileReader();
                        fileReader.onload = function (event) {
                            showPicture.src = event.target.result;
                            $('#preview').show();
                        };
                        fileReader.readAsDataURL(file);
                    }
                    catch (e) {
                        //
                        var error = document.querySelector("#error");
                        if (error) {
                            error.innerHTML = "Neither createObjectURL or FileReader are supported";
                        }
                    }
                }
            }
        };
    }
})();

function autocomplete(selector, doc_field, doc_type) {
        $(selector).select2({
            placeholder: '',
            allowClear: true,
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
    };

    autocomplete('#subjects', 'subjects', 'adsubmit');