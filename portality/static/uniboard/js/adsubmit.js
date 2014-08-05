jQuery(document).ready(function($) {

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
                var data = {id: element.val().toLowerCase(), text: element.val().toLowerCase()};
                callback(data);
            }
        });
    };

    $('#price').change(function () {
        var high_number = 60;

        if ($('#price').val() > high_number){
            alert('Are you sure you want to set such a high price?');
        }

    })();

    autocomplete('#subjects', 'subject', 'adsubmit');

    $("#keywords").select2({tags: [], formatNoMatches: function(term) { return "enter your keyword" }})
    $('#condition').select2();
    $('#location').select2();

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

        $("#placeholder").show();
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
                        $("#placeholder").hide()
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
                                $("#placeholder").hide()
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





});