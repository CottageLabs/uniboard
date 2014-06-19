# UniBoard

## Installation

UniBoard depends on esprit, which must be installed before this package will install:

https://github.com/richard-jones/esprit

It also contains submodules, so when you check this code out you will also need to run:

    git submodule init
    git submidule update

It also relies on the Google Map API, so in order to view the maps you will need a Google API key:

https://developers.google.com/maps/documentation/javascript/tutorial#api_key

and you will need to add a file at the root of the application (same directory as this README) called app.cfg with the content:

GOOGLE_MAP_API_KEY="<your key>"

## Data Models

### Account Data Model

    {
        "id" : "<opaque id for the user>",
        "email" : "<institutional email address>",
        "name" : "<user's full name>",
        "degree" : "<degree name>",
        "postcode" : "<uk postcode>",
        "loc" : {
            "lat" : <latitude>,
            "lon" : <longitude>
        },
        "phone" : "<user's preferred phone number>",
        "graduation" : <year of graduation>,
        "password" : "<hashed password>",
        "admin" : {
            "deleted" : True/False,
            "banned" : True/False
        },
        "role" : ["<user role>"],
        "reset_token" : "<password reset token>",
        "reset_expires" : "<password reset token expiration timestamp>",
        "activation_token" : "<account activation token>",
        "activation_expires" : "<account activation token expiration timestamp>",
        "created_date" : "<date account was created>",
        "last_updated" : "<date account was last modified>"
    }

* We are not breaking down the name into first/last, as this can just become a hassle to manage
* The "loc" field will be a geopoint in the ES index, which will allow us to do geo-location, distance searching, etc
* "graduation" should be a 4 digit year as a number

### Advert (Seller) Data Model

    {
        "id" : "<opaque identifier for the advert>",
        "owner" : "<user who created the ad>",
        "isbn" : ["<isbn-10>", "<isbn-13>"],
        "title" : "<book title>",
        "edition" : "<edition of book>",
        "authors" : "<authors>",
        "year" : <year of publication>,
        "publisher" : "<publisher of book>",
        "image_id" : "<id of book image in image library>",
        "subject" : ["<subject classification>"],
        "condition" : "<condition of the book>",
        "loc" : {
            "lat" : <latitude>,
            "lon" : <longitude>
        },
        "spot" : "<location of sale>"
        "keywords" : ["<keyword>"],
        "price" : <price in GBP>,
        "admin" : {
            "deleted" : True/False,
            "reactivate_token" : "<reactivate token>",
            "reactivate_expires" : "<ractivate token expiration timestamp>",
            "expires" : "<date the advert expires>",
            "abuse" : <number of times abuse reported>
        },
        "created_date" : "<date advert was created>",
        "last_updated" : "<date advert was last modified>",
    }

* we make space for multiple isbns in case there's a need for both isbn10 and isbn13 numbers.
* "authors" is free-text, because this is not a bibliographic service - users will just want to put a string in
* "year" should be a 4 digit year as a number
* "image_id" will be some opaque id for an object in the image directory
* The "loc" field will be a geopoint in the ES index, which will allow us to do geo-location, distance searching, etc
* "price" should be a float
* "abuse" should be an int, which indicates the number of times this advert has been flagged

## API

### Create/Edit an Advert

accessible by: user

    POST /advert
    [advert object]

Send an advert object which complies with the above Data Model.  If the record contains an id, it will overwrite
any existing advert, otherwise a new one will be created.

The record should omit the following fields, as they will be ignored:
    * admin
    * created_date
    * last_updated

Returns 201 or 200 (depending on created/edited), and body content

    {
        "action" : "<created/edited>",
        "id" : "<id of advert created/edited>",
        "loc" : "<url for advert if it has been made public>"
    }

Create/Edit can go ahead if:

* user is authenticated
* user has role "create_advert"

### Delete an Advert

accessible by: admin, user (if they are the owner)

    DELETE /advert/<advert_id>

or

    POST /advert/<advert_id>
    {"delete" : True}

Send a delete request to the advert with the specified id.  This will cause the advert to be soft-deleted.

Returns a 204

Delete can go ahead if

* user is authenticated
* user is admin or user is owner of advert
* user has "delete_advert" role

### Report Abuse

accessible by: user

    POST /advert/<advert_id>/abuse

Send an abuse notification regarding the advert with the specified id.  This will cause the advert's abuse counter
to climb by one.

Returns a 204

Report abuse can go ahead if

* user is authenticated
* user has "report_abuse" role

### Resources

The institutional emails are checked against a JSON file. The same file is used for mapping university domains to university addresses.
