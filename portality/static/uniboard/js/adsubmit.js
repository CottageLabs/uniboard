jQuery(document).ready(function($) {

    function bookForm() {
        $("#book_advert").show()
        $("#other_advert").hide()
        $("#show_other_form").parent().removeClass("active")
        $("#show_book_form").parent().addClass("active")
    }

    function generalForm() {
        $("#book_advert").hide()
        $("#other_advert").show()
        $("#show_book_form").parent().removeClass("active")
        $("#show_other_form").parent().addClass("active")
    }

    // functions to switch between the two different kinds of input form
    $("#show_book_form").click(function(event) {
        event.preventDefault()
        if ($(this).attr("data-disabled") === "true") {
            return
        }
        bookForm()
    })

    $("#show_other_form").click(function(event) {
        event.preventDefault()
        if ($(this).attr("data-disabled") === "true") {
            return
        }
        generalForm()
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
                var data = {id: element.val(), text: element.val()};
                callback(data);
            }
        });
    };

    // sense check the price
    $('.book_price').change(function () {
        if ($('.book_price').val() > price_check_book){
            alert('Are you sure you want to set such a high price?');
        }
    });

    $('.general_price').change(function () {
        if ($('.general_price').val() > price_check_general){
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
                        // URL.revokeObjectURL(imgURL);
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

    function enableBookEntry() {
        $("#book_metadata").show()
        $("#book_submit_buttons").show()
        $("#no_isbn").hide()
    }

    $("#no_isbn").click(function(event) {
        event.preventDefault()
        $("#book_metadata").show()
        $("#book_submit_buttons").show()
        $(this).hide()
    })

    $("#fetch_book_data").click(function(event) {
        event.preventDefault()

        function gotISBN(data) {
            if (Object.keys(data).length === 0) {
                alert("Could not locate any data associated with that ISBN")
                enableBookEntry()
                return
            }

            if (data.title) {
                $("#adsubmitform input[name=title]").val(data.title)
            }
            if (data.authors) {
                var author_string = data.authors.join(", ")
                $("#adsubmitform input[name=authors]").val(author_string)
            }
            if (data.publisher) {
                $("#adsubmitform input[name=publisher]").val(data.publisher)
            }
            if (data.subjects && data.subjects.length > 0) {
                $("#adsubmitform input[name=subject]").select2("val", data.subjects[0])
            }

            enableBookEntry()
        }

        function failedISBN(data) {
            alert("Could not locate any data associated with that ISBN")
            enableBookEntry()
        }

        var isbn = $("#isbn").val()
        $.ajax({
            url: "/isbn/" + isbn,
            method: "GET",
            success : gotISBN,
            error: failedISBN
        })
    })

    // if an isbn is entered in the form, always enable the book data
    if ($("#isbn").val()) {
        enableBookEntry()
    }

    // once all the stuff has been defined, make sure we're looking at the right thing
    if (editing) {
        if (is_book) {
            enableBookEntry()
            bookForm()
        } else {
            generalForm()
        }
    }

});