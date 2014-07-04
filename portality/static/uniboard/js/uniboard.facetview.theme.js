jQuery(document).ready(function($) {
    
    /****************************************************************
     * Uniboard FacetView theme
     ***************************
     * Requires the following variables to be in scope
     *
     * user_lat - the latitude of the user of the view
     * user_lon - the longitude of the user of the view
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
            result += "<br>"
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

    var facets = [
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
    ]
    if (user_lat && user_lon) {
        facets.push({
            'field' : 'loc',
            'display' : 'Distance from my term-time residence',
            'type' : 'geo_distance',
            'open' : true,
            'hide_empty_distance' : true,
            'unit' : 'mi',
            'lat' : user_lat,
            'lon' : user_lon,
            "distance" : [
                {"to" : 0.5, "display" : "within 0.5 miles"},
                {"to" : 2, "display" : "within 2 miles"},
                {"to" : 5, "display" : "within 5 miles"},
                {"to" : 10, "display" : "within 10 miles"},
                {"to" : 20, "display" : "within 20 miles"},
                {"to" : 50, "display" : "within 50 miles"}
            ]
        })
    }
    facets.push({'field': 'subject.exact', 'display': 'Subject'})
    facets.push({'field': 'condition.exact', 'display': 'Condition'})
    facets.push({'field': 'year', 'display': 'Publication Year'})
    facets.push({'field': 'edition.exact', 'display': 'Edition'})
    
    $('#facetview').facetview({
        debug: false,
        search_url : current_scheme + "//" + current_domain + "/user_query/searchable,ad/_search",
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
        
    });
    
});

