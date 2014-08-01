jQuery(document).ready(function($) {
    
    /****************************************************************
     * Uniboard FacetView theme
     ***************************
     * Requires the following variables to be in scope
     *
     * user_lat - the latitude of the user of the view
     * user_lon - the longitude of the user of the view
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


    function uniSearchOptions(options) {
        /*****************************************
         * overrides must provide the following classes and ids
         *
         * class: facetview_startagain - reset the search parameters
         * class: facetview_pagesize - size of each result page
         * class: facetview_order - ordering direction of results
         * class: facetview_orderby - list of fields which can be ordered by
         * class: facetview_searchfield - list of fields which can be searched on
         * class: facetview_freetext - input field for freetext search
         *
         * should (not must) respect the following configs
         *
         * options.search_sortby - list of sort fields and directions
         * options.searchbox_fieldselect - list of fields search can be focussed on
         * options.sharesave_link - whether to provide a copy of a link which can be saved
         */

        // initial button group of search controls
        var thefacetview = '<div class="btn-group" style="display:inline-block; margin-right:5px;"> \
            <a class="btn btn-small facetview_startagain" title="clear all search settings and start again" href=""><i class="icon-remove"></i></a> \
            <a class="btn btn-small facetview_pagesize" title="change result set size" href="#"></a>';

        if (options.search_sortby.length > 0) {
            thefacetview += '<a class="btn btn-small facetview_order" title="current order descending. Click to change to ascending" \
                href="desc"><i class="icon-arrow-down"></i></a>';
        }
        thefacetview += '</div>';

        // selection for search ordering
        if (options.search_sortby.length > 0) {
            thefacetview += '<select class="facetview_orderby" style="border-radius:5px; \
                -moz-border-radius:5px; -webkit-border-radius:5px; width:100px; background:#eee; margin:0 5px 21px 0;"> \
                <option value="">order by ... relevance</option>';

            for (var each = 0; each < options.search_sortby.length; each++) {
                var obj = options.search_sortby[each];
                var sortoption = '';
                if ($.type(obj['field']) == 'array') {
                    sortoption = sortoption + '[';
                    sortoption = sortoption + "'" + obj['field'].join("','") + "'";
                    sortoption = sortoption + ']';
                } else {
                    sortoption = obj['field'];
                }
                thefacetview += '<option value="' + sortoption + '">' + obj['display'] + '</option>';
            };
            thefacetview += '</select>';
        }

        // select box for fields to search on
        if ( options.searchbox_fieldselect.length > 0 ) {
            thefacetview += '<select class="facetview_searchfield" style="border-radius:5px 0px 0px 5px; \
                -moz-border-radius:5px 0px 0px 5px; -webkit-border-radius:5px 0px 0px 5px; width:100px; margin:0 -2px 21px 0; background:#ecf4ff;">';
            thefacetview += '<option value="">search all</option>';

            for (var each = 0; each < options.searchbox_fieldselect.length; each++) {
                var obj = options.searchbox_fieldselect[each];
                thefacetview += '<option value="' + obj['field'] + '">' + obj['display'] + '</option>';
            };
            thefacetview += '</select>';
        };

        // text search box
        thefacetview += '<input type="text" class="facetview_freetext span4" style="display:inline-block; margin:0 0 21px 0; background:#ecf4ff;" name="q" \
            value="" placeholder="search term" />';

        // share and save link
        if (options.sharesave_link) {
            thefacetview += '<a class="btn btn-info facetview_sharesave pull-right" title="share a link to this search" style="margin:0 0 21px 5px;" href="">share <i class="icon-white icon-share-alt"></i></a>';
            thefacetview += '<div class="facetview_sharesavebox alert alert-info" style="display:none;"> \
                <button type="button" class="facetview_sharesave close">×</button> \
                <p>Share or save this search:</p> \
                <textarea class="facetview_sharesaveurl" style="width:100%;height:100px;">' + shareableUrl(options) + '</textarea> \
                </div>';
        }
        return thefacetview
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
        render_search_options : uniSearchOptions
    });
    
});

