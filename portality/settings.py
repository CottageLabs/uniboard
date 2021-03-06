import os
from esprit import mappings

# ========================
# MAIN SETTINGS

# base path, to the directory where this settings file lives
BASE_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
IMAGES_FOLDER = os.path.join(BASE_FILE_PATH, 'user_uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

#Host url
LOCALHOST_URL = "http://www.brunel.uni-board.co.uk"

#Price checks
PRICE_CHECK_BOOK = 60
PRICE_CHECK_OTHER = 100

# make this something secret in your overriding app.cfg
SECRET_KEY = "default-key"

# contact info
ADMIN_NAME = "UniBoard"
ADMIN_EMAIL = "sysadmin@cottagelabs.com"
BCC_EMAIL = "emanuil@cottagelabs.com"
ADMINS = ["emanuil@cottagelabs.com", "richard@cottagelabs.com"]
SUPPRESS_ERROR_EMAILS = False  # should be set to False in production and True in staging

# service info
SERVICE_NAME = "UniBoard"
SERVICE_TAGLINE = ""
HOST = "0.0.0.0"
DEBUG = True
PORT = 5011
SSL = False

# elasticsearch settings
ELASTIC_SEARCH_HOST = "http://localhost:9200" # remember the http:// or https://
#ELASTIC_SEARCH_HOST = "http://93.93.131.168:9200"
ELASTIC_SEARCH_DB = "uniboard"
INITIALISE_INDEX = True # whether or not to try creating the index and required index types on startup

# can anonymous users get raw JSON records via the query endpoint?
PUBLIC_ACCESSIBLE_JSON = True 

# =======================
# email settings

SMTP_SERVER = "smtp.mandrillapp.com"

SMTP_PORT = 587

# override these in your app.cfg, and don't put them in version control
SMTP_USER = None
SMTP_PASS = None

# ========================
# user login settings

# amount of time a reset token is valid for (86400 is 24 hours)
PASSWORD_RESET_TIMEOUT = 86400
PASSWORD_ACTIVATE_TIMEOUT = PASSWORD_RESET_TIMEOUT * 14

# ========================
# authorisation settings

# Can people register publicly? If false, only the superuser can create new accounts
# PUBLIC_REGISTER = False

SUPER_USER_ROLE = "admin"

# FIXME: something like this required for hierarchical roles, but not yet needed
#ROLE_MAP = {
#    "admin" : {"publisher", "create_user"}
#}

# ========================
# MAPPING SETTINGS

# a dict of the ES mappings. identify by name, and include name as first object name
# and identifier for how non-analyzed fields for faceting are differentiated in the mappings
FACET_FIELD = ".exact"

"""
MAPPINGS = {
    "account" : {
        "account" : {
            "dynamic_templates" : [
                {
                    "default" : {
                        "match" : "*",
                        "match_mapping_type": "string",
                        "mapping" : {
                            "type" : "multi_field",
                            "fields" : {
                                "{name}" : {"type" : "{dynamic_type}", "index" : "analyzed", "store" : "no"},
                                "exact" : {"type" : "{dynamic_type}", "index" : "not_analyzed", "store" : "yes"}
                            }
                        }
                    }
                }
            ]
        }
    }
}
MAPPINGS['advert'] = {'advert':MAPPINGS['account']['account']}
"""

MAPPINGS = {
    "account" : mappings.for_type(
        "account",
            mappings.properties(mappings.type_mapping("loc", "geo_point")),
            mappings.dynamic_templates(
            [
                mappings.EXACT,
                mappings.dynamic_type_template("geo", "loc", mappings.make_mapping("geo_point"))
            ]
        )
    ),
    "advert" : mappings.for_type(
        "advert",
            mappings.properties(mappings.type_mapping("loc", "geo_point")),
            mappings.dynamic_templates(
            [
                mappings.EXACT,
                mappings.dynamic_type_template("geo", "loc", mappings.make_mapping("geo_point"))
            ]
        )
    )
}


# ========================
# QUERY SETTINGS

# list index types that should not be queryable via the query endpoint
NO_QUERY = []
SU_ONLY = ["account"]

# list additional terms to impose on anonymous users of query endpoint
# for each index type that you wish to have some
# must be a list of objects that can be appended to an ES query.bool.must
# for example [{'term':{'visible':True}},{'term':{'accessible':True}}]
ANONYMOUS_SEARCH_TERMS = {
    # "pages": [{'term':{'visible':True}},{'term':{'accessible':True}}]
}

# a default sort to apply to query endpoint searches
# for each index type that you wish to have one
# for example {'created_date' + FACET_FIELD : {"order":"desc"}}
DEFAULT_SORT = {
    # "pages": {'created_date' + FACET_FIELD : {"order":"desc"}}
}

QUERY_ROUTE = {
    "user_query" : {"role": "user", "default_filter": True},
    "admin_query" : {"role" : "admin", "default_filter": False}
#    "publisher_query" : {"role" : "publisher", "default_filter" : False, "owner_filter" : True}
}

# ==========================
# ADVERT SETTINGS

# amount of time that adverts have before they timeout
# 604800 = 7 days
ADVERT_TIMEOUT = 604800

# ==========================
# MAP INTEGRATION

# add this in app.cfg
GOOGLE_MAP_API_KEY = None


# ===========================
# Feedback

FEEDBACK_EMAIL = "enquiry@uni-board.co.uk"
