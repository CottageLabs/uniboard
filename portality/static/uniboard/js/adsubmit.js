jQuery(document).ready(function($) {

    // functions to switch between the two different kinds of input form
    $("#show_book_form").click(function(event) {
        event.preventDefault()
        $("#book_advert").show()
        $("#other_advert").hide()
        $("#show_other_form").parent().removeClass("active")
        $(this).parent().addClass("active")
    })

    $("#show_other_form").click(function(event) {
        event.preventDefault()
        $("#book_advert").hide()
        $("#other_advert").show()
        $("#show_book_form").parent().removeClass("active")
        $(this).parent().addClass("active")
    })

    // generic autocomplete function

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

    // sense check the price
    $('.price').change(function () {
        var high_number = 60;

        if ($('.price').val() > price_check_book){
            alert('Are you sure you want to set such a high price?');
        }

    });

    // autocompletes required by either form
    autocomplete('#subject', 'subject', 'adsubmit');
    autocomplete('#category', 'category', 'adsubmit')

    // enable keyword entry on the relevant fields
    $(".keywords").select2({tags: [], tokenSeparators: [",", " "], formatNoMatches: function(term) { return "enter your keyword" }})

    // apply select2 to the condition and the location
    $('.condition').select2();
    $('.location').select2();

    // hide the postcode containers
    $('#book_postcode').hide();
    $("#general_postcode").hide();

    // bind show/hide functions for the postcode containers
    $('#book_location').change(function(e){
      if ($('#book_location').val() == 'postcode'){
        $('#book_postcode').show();
      }else{
        $('#book_postcode').hide();
      }
    });

    $('#general_location').change(function(e){
      if ($('#general_location').val() == 'postcode'){
        $('#general_postcode').show();
      }else{
        $('#general_postcode').hide();
      }
    });

    function pictureUpload(take_picture_selector, show_picture_selector, placeholder_selector, preview_selector) {
        var takePicture = document.querySelector(take_picture_selector);
        var showPicture = document.querySelector(show_picture_selector);

        $(placeholder_selector).show();
        $(preview_selector).hide();

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
                        $(placeholder_selector).hide()
                        $(preview_selector).show();

                        // Revoke ObjectURL
                        URL.revokeObjectURL(imgURL);
                    }
                    catch (e) {
                        try {
                            // Fallback if createObjectURL is not supported
                            var fileReader = new FileReader();
                            fileReader.onload = function (event) {
                                showPicture.src = event.target.result;
                                $(placeholder_selector).hide()
                                $(preview_selector).show();
                            };
                            fileReader.readAsDataURL(file);
                        }
                        catch (e) {
                            // fixme: it looks to me like this doesn't write to anywhere in the current template
                            var error = document.querySelector("#error");
                            if (error) {
                                error.innerHTML = "Neither createObjectURL or FileReader are supported";
                            }
                        }
                    }
                }
            };
        }
    }

    pictureUpload("#take-picture", "#show-picture", "#placeholder", "#preview")
    pictureUpload("#general_take-picture", "#general_show-picture", "#general_placeholder", "#general_preview")

/*
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
    */

});