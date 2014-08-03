jQuery(document).ready(function($) {
    
    /****************************************************************
     * Uniboard Admin FacetView theme
     ***************************
     * Requires the following variables to be in scope
     *
     * img_path - path to image service
     */
    
    function discoveryRecordView(options, record) {
        var result = options.resultwrap_start;

        result += "<div class='row-fluid' style='margin-top: 10px; margin-bottom: 10px'>"

        // build the result
        result += "<div class='span2'>"
        if (record.image_id) {
            result += "<img src='" + img_path + record.image_id + "'>"
        } else {
            result += "<img src='/static/uniboard/img/book_placeholder.png'>"
        }
        result += "</div>"

        result += "<div class='span8'>"
        result += "<div style='padding-bottom: 10px'><strong><a href='/advert/" + record.id + "' style='font-size: 200%'>" + record.title + "</a></strong></div>"

        // the bibliographic data associated with the book
        if (record.authors) {
            result += "<em style='font-size: 150%; color: #666666'>" + record.authors + "</em><br>"
        }
        if (record.publisher) {
            result += "Publisher: " + record.publisher + "&nbsp;&nbsp;"
        }
        if (record.year) {
            result += "Publication Year: " + record.year + "&nbsp;&nbsp;"
        }
        if (record.edition) {
            result += "Edition: " + record.edition + "&nbsp;&nbsp;"
        }
        if (record.publisher || record.year || record.edition) {
            result += "<br><br>"
        }

        // the administrative data associated with the book
        if (record.admin && (record.admin.hasOwnProperty("abuse"))) {
            if (record.admin.abuse === 0) {
                result += '<span>No Abuse Reported</span>'
            } else {
                result += '<span style="font-weight: bold; color: #cc3333">Abuse Reported " + record.admin.abuse + " Times</span>'
            }
            result += "&nbsp;&nbsp;"
        }

        if (record.admin && (record.admin.hasOwnProperty("deactivated"))) {
            if (record.admin.deactivated) {
                result += '<span style="font-weight: bold; color: #cc3333">Deactivated</span>'
            } else {
                result += '<span style="font-weight: bold; color: #33cc33">Active</span>'
            }
            result += "&nbsp;&nbsp;"
        }

        if (record.admin && (record.admin.hasOwnProperty("deleted"))) {
            if (record.admin.deleted) {
                result += '<span style="font-weight: bold; color: #cc3333">Deleted</span>'
            } else {
                result += '<span style="font-weight: bold; color: #33cc33">Not deleted</span>'
            }
            result += "&nbsp;&nbsp;"
        }

        if (record.admin && (record.admin.hasOwnProperty("expires"))) {
            result += "Advert expires on: " + record.admin.expires
            result += "&nbsp;&nbsp;"
        }

        result += "</div>"

        result += "<div class='span2'>"
        if (record.price) {
            var bits = String(record.price).split(".")
            var pounds = bits[0]
            var pence = "00"
            if (bits.length > 1) {
                pence = bits[1]
                if (pence.length === 1) {
                    pence += "0"
                }
            }
            result += "<div style='padding-top: 15px'>"
            result += "<span style='font-size: 300%; font-weight: bold'>£" + pounds + ".</span>"
            result += "<span style='font-size: 200%; font-weight: bold'>" + pence + "</span>"
            result += "</div>"
        }
        result += "</div>"

        result += "</div>"
        result += options.resultwrap_end;
        return result;
    }

    var facets = []
    facets.push({"field" : "admin.deleted", "display" : "Deleted?", "open" : true})
    facets.push({"field" : "admin.deactivated", "display" : "Deactivated?", "open" : true})
    facets.push({"field" : "admin.abuse", "display" : "Times abuse reported", "open" : true})
    facets.push(
        {
            'field': 'price',
            'display': 'Price',
            "type" : "range",
            "open" :true,
            "hide_empty_range" : true,
            "range" : [
                {"to" : 5, "display" : "less than £5"},
                {"from" : 5, "to" : 10, "display": "£5 - £10"},
                {"from" : 10, "to" : 20, "display": "£10 - £20"},
                {"from" : 20, "to" : 30, "display": "£20 - £30"},
                {"from" : 30, "to" : 40, "display": "£30 - £40"},
                {"from" : 40, "to" : 50, "display": "£40 - £50"},
                {"from" : 50, "display": "£50+"}
            ]
        }
    )
    facets.push({'field': 'subject.exact', 'display': 'Subject'})
    facets.push({'field': 'condition.exact', 'display': 'Condition'})
    facets.push({'field': 'year', 'display': 'Publication Year'})
    facets.push({'field': 'edition.exact', 'display': 'Edition'})
    
    $('#facetview').facetview({
        debug: false,
        search_url : current_scheme + "//" + current_domain + "/admin_query/searchable,ad/_search",
        page_size : 25,
        facets : facets,
        search_sortby : [
            {'display':'Date added','field':'created_date'},
            {'display':'Title','field':'title.exact'},
            {'display':'Publication Year','field':'year'},
            {'display':'Edition','field':'edition.exact'},
            {'display':'Price','field':'price'}
        ],
        searchbox_fieldselect : [
            {'display':'Title','field':'title'},
            {'display':'ISBN','field':'isbn'},
            {'display':'Authors','field':'authors'},
            {'display':'Publisher','field':'publisher'}
        ],
        render_result_record : discoveryRecordView,
        search_button: true,
        sharesave_link: false
    });
    
});

