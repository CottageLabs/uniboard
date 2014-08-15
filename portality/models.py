import sys
from portality.authorise import Authorise
from portality import dao
from portality.core import app
import uuid
from datetime import datetime, timedelta

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin


def lookup_model(name='', capitalize=True):
    if capitalize:
        name = name.capitalize()
    try:
        return getattr(sys.modules[__name__], name)
    except:
        return None

class ModelException(Exception):
    pass

class Account(dao.AccountDAO, UserMixin):
    """
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
    """
    # we are not having usernames (people are identified by email address), so we either
    # want to use their email address as their id, or mint them an opaque id.
    @classmethod
    def make_account(cls, username, name=None, email=None, degree=None, postcode=None, phone=None, graduation=None, roles=[]):
        a = cls.pull(username)
        if a:
            return a

        a = Account()
        a.id = email
        a.set_name(name) if name else None
        #a.set_email(email) if email else None
        a.set_degree(degree) if degree else None
        #a.set_location(lat,lon) if postcode else None
        a.set_phone(phone) if phone else None
        a.set_graduation(graduation) if graduation else None
        for role in roles:
            a.add_role(role)
        
        activation_token = uuid.uuid4().hex
        # give them 14 days to create their first password if timeout not specified in config
        a.set_activation_token(activation_token, app.config.get("PASSWORD_CREATE_TIMEOUT", app.config.get('PASSWORD_RESET_TIMEOUT', 86400) * 14))
        return a
    
    @property
    def name(self):
        return self.data.get("name")
    
    def set_name(self, val):
        self.data["name"] = val
    
    @property
    def email(self):
        return self.data.get("email")

    def set_email(self, val):
        self.data["email"] = val

    def set_password(self, password):
        self.data['password'] = generate_password_hash(password)

    def check_password(self, password):
        if "password" not in self.data:
            return False
        return check_password_hash(self.data['password'], password)

    def clear_password(self):
        if "password" in self.data:
            del self.data["password"]

    @property
    def degree(self):
        return self.data.get("degree")

    def set_degree(self, val):
        self.data["degree"] = val

    @degree.deleter
    def degree(self):
        if "degree" in self.data:
            del self.data["degree"]

    @property
    def postcode(self):
        return self.data.get("postcode")

    def set_postcode(self, val):
        self.data["postcode"] = val

    @postcode.deleter
    def postcode(self):
        if "postcode" in self.data:
            del self.data["postcode"]

    @property
    def location(self):
        loc = self.data.get("loc")
        if loc is None:
            return None
        return (loc.get("lat"), loc.get("lon"))

    def set_location(self, lat, lon):
        if "loc" not in self.data:
            self.data["loc"] = {}
        try:
            lat = float(lat)
            lon = float(lon)
        except:
            raise ModelException("Unable to set lat and lon - must be floats or cast to float: " + str(lat) + ", " + str(lon))
        self.data["loc"]["lat"] = lat
        self.data["loc"]["lon"] = lon

    def unset_location(self):
        if "loc" in self.data:
            del self.data["loc"]

    @property
    def lat(self):
        loc = self.location
        if loc:
            return loc[0]
        return None

    @property
    def lon(self):
        loc = self.location
        if loc:
            return loc[1]
        return None
    
    @property
    def phone(self):
        return self.data.get("phone")

    def set_phone(self, val):
        self.data["phone"] = val

    @phone.deleter
    def phone(self):
        if "phone" in self.data:
            del self.data["phone"]

    @property
    def graduation(self):
        return self.data.get("graduation")

    def set_graduation(self, val):
        try:
            val = int(val)
        except:
            raise ModelException("Unable to set graduation year - must be int or cast to int: " + str(val))
        if len(str(val)) != 4:
            raise ModelException("Unable to set graduation year - must be 4 digit format: " + str(val))
        self.data["graduation"] = val

    @graduation.deleter
    def graduation(self):
        if "graduation" in self.data:
            del self.data["graduation"]

    def is_deleted(self):
        return self.data.get("admin", {}).get("deleted", False)

    def set_deleted(self, val, cascade=True, save=True):
        if type(val) != bool:
            raise ModelException("Unable to set deleted - must be boolean value")
        if "admin" not in self.data:
            self.data["admin"] = {}
        self.data["admin"]["deleted"] = val

        # Note that if val=False, we do not un-delete the adverts, this is a one-way operation
        if cascade and val: # if we are deleting the account
            adverts = Advert.get_by_owner(self.id)
            for ad in adverts:
                ad.mark_deactivated(True)
                ad.save()

        if save:
            self.save()

    def is_banned(self):
        return self.data.get("admin", {}).get("banned", False)

    def set_banned(self, val):
        if type(val) != bool:
            raise ModelException("Unable to set banned - must be boolean value")
        if "admin" not in self.data:
            self.data["admin"] = {}
        self.data["admin"]["banned"] = val

    @property
    def reset_token(self):
        return self.data.get('reset_token')

    def set_reset_token(self, token, timeout):
        expires = datetime.now() + timedelta(0, timeout)
        self.data["reset_token"] = token
        self.data["reset_expires"] = expires.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def remove_reset_token(self):
        if "reset_token" in self.data:
            del self.data["reset_token"]
        if "reset_expires" in self.data:
            del self.data["reset_expires"]

    @property
    def activation_token(self):
        return self.data.get('activation_token')

    def set_activation_token(self, token, timeout):
        expires = datetime.now() + timedelta(0, timeout)
        self.data["activation_token"] = token
        self.data["activation_expires"] = expires.strftime("%Y-%m-%dT%H:%M:%SZ")

    def remove_activation_token(self):
        if "activation_token" in self.data:
            del self.data["activation_token"]
        if "activation_expires" in self.data:
            del self.data["activation_expires"]

    @property
    def is_super(self):
        # return not self.is_anonymous() and self.id in app.config['SUPER_USER']
        return Authorise.has_role(app.config["SUPER_USER_ROLE"], self.data.get("role", []))
    
    def has_role(self, role):
        return Authorise.has_role(role, self.data.get("role", []))
    
    def add_role(self, role):
        if "role" not in self.data:
            self.data["role"] = []
        if role not in self.data:
            self.data["role"].append(role)
    
    @property
    def role(self):
        return self.data.get("role", [])
    
    def set_role(self, role):
        if not isinstance(role, list):
            role = [role]
        self.data["role"] = role

class Advert(dao.AdvertDAO):
    """
    {
        "id" : "<opaque identifier for the advert>",
        "owner" : "<user who created the ad>",
        "category" : "<Book or something else>",
        "isbn" : ["<isbn-10>", "<isbn-13>"],
        "title" : "<book title>",
        "description" : "<description of the object for sale>",
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
    """

    # special category which represents a book
    BOOK = "Book"

    @property
    def owner(self): return self.data.get("owner")
    def set_owner(self, val): self.data["owner"] = val

    @property
    def category(self): return self.data.get("category")
    def set_category(self, val): self.data["category"] = val

    @property
    def isbn(self): return self.data.get("isbn", [])

    def set_isbn(self, val):
        if not isinstance(val, list):
            val = [val]
        self.data["isbn"] = val

    def add_isbn(self, val):
        if "isbn" not in self.data:
            self.data["isbn"] = []
        self.data["isbn"].append(val)

    @property
    def title(self): return self.data.get("title", "")
    def set_title(self, val): self.data["title"] = val

    @property
    def description(self): return self.data.get("description", "")
    def set_description(self, val): self.data["description"] = val

    @property
    def edition(self): return self.data.get("edition", "")

    def set_edition(self, val): self.data["edition"] = val

    @property
    def authors(self): return self.data.get("authors", "")

    def set_authors(self, val): self.data["authors"] = val

    @property
    def year(self): return self.data.get("year", "")

    def set_year(self, val):
        try:
            val = int(val)
        except:
            raise ModelException("Unable to set publication year - must be int or cast to int: " + str(val))
        self.data["year"] = val

    @property
    def publisher(self): return self.data.get("publisher", "")

    def set_publisher(self, val): self.data["publisher"] = val

    @property
    def image_id(self): return self.data.get("image_id")

    def set_image_id(self, val): self.data["image_id"] = val

    @property
    def subjects(self): return self.data.get("subject", [])

    @property
    def subject(self):
        if 'subject' not in self.data:
            return ''
        else:
            return self.data["subject"][0]

    def add_subject(self, val):
        if "subject" not in self.data:
            self.data["subject"] = []
        self.data["subject"].append(val)

    def set_subjects(self, val):
        if not isinstance(val, list):
            val = [val]
        self.data["subject"] = val

    @property
    def condition(self): return self.data.get("condition", "")

    def set_condition(self, val): self.data["condition"] = val

    @property
    def spot(self):
        return self.data.get("spot")

    def set_spot(self, val):
        self.data["spot"] = val

    @property
    def location(self):
        loc = self.data.get("loc")
        if loc is None:
            return None
        return (loc.get("lat"), loc.get("lon"))

    @property
    def lat(self):
        return self.location[0]

    @property
    def lon(self):
        return self.location[1]

    def set_location(self, lat, lon):
        if "loc" not in self.data:
            self.data["loc"] = {}
        try:
            lat = float(lat)
            lon = float(lon)
        except:
            raise ModelException("Unable to set lat and lon - must be floats or cast to float: " + str(lat) + ", " + str(lon))
        self.data["loc"]["lat"] = lat
        self.data["loc"]["lon"] = lon

    @property
    def keywords(self): return self.data.get("keywords", [])

    def add_keyword(self, val):
        if "keywords" not in self.data:
            self.data["keywords"] = []
        self.data["keywords"].append(val)

    def set_keywords(self, val):
        if not isinstance(val, list):
            val = [val]
        self.data["keywords"] = val

    @property
    def price(self):
        p = self.data.get("price")
        if p is None:
            return None
        return "%.2f" % p

    def set_price(self, val):
        try:
            val = float(val)
        except:
            raise ModelException("Unable to set price - must be float or cast to float: " + str(val))
        self.data["price"] = val

    def _admin(self, key, default=None):
        return self.data.get("admin", {}).get(key, default)

    def _set_admin(self, key, value):
        if "admin" not in self.data:
            self.data["admin"] = {}
        self.data["admin"][key] = value

    @property
    def is_deleted(self):
        return self._admin("deleted", False)

    def mark_deleted(self, val=True):
        if type(val) != bool:
            raise ModelException("Unable to mark deleted - must be bool: " + str(val))
        self._set_admin("deleted", val)
        # if we are deleting the advert then also deactivate it.  But if we are
        # undeleting the advert, leave it deactivated
        if val:
            self.mark_deactivated()

    @property
    def is_deactivated(self):
        return self._admin("deactivated", False)

    def mark_deactivated(self, val=True):
        if type(val) != bool:
            raise ModelException("Unable to mark deactivated - must be bool: " + str(val))
        self._set_admin("deactivated", val)

    @property
    def expires(self): return self._admin("expires")

    def set_expires(self, val):
        try:
            dt = datetime.strptime(val, "%Y-%m-%dT%H:%M:%SZ")
        except:
            raise ModelException("Unable to parse date " + str(val) + " - must be of the form %Y-%m-%dT%H:%M:%SZ")
        self._set_admin("expires", val)

    def expires_in(self, timeout):
        expires = datetime.now() + timedelta(0, timeout)
        self._set_admin("expires", expires.strftime("%Y-%m-%dT%H:%M:%SZ"))

    @property
    def is_expired(self):
        dt = datetime.strptime(self.expires, "%Y-%m-%dT%H:%M:%SZ")
        return dt <= datetime.now()

    @property
    def abuse(self): return self._admin("abuse", 0)

    @property
    def last_updated(self): return self.data.get("last_updated")

    def get_last_updated(self, format="%Y-%m-%dT%H:%M:%SZ"):
        dt = datetime.strptime(self.last_updated, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime(format)

    def increment_abuse(self, by=1):
        ab = self._admin("abuse", 0)
        ab += by
        self._set_admin("abuse", ab)

    def prep(self):
        dact = self._admin("deactivated")
        if dact is None:
            self.mark_deactivated(False)

        d = self._admin("deleted")
        if d is None:
            self.mark_deleted(False)

        e = self._admin("expires")
        if e is None:
            timeout = app.config.get("ADVERT_TIMEOUT", 604800)
            self.expires_in(timeout)

        a = self._admin("abuse")
        if a is None:
            self._set_admin("abuse", 0)

    def save(self, conn=None, makeid=True, created=True, updated=True):
        self.prep()
        super(Advert, self).save(conn, makeid, created, updated)

# NOTE: this is a workaround for auto-mapping from the url scheme to an object
# which does not contain the word "advert" as this messes with AdBlock Plus's
# ad detection
class SearchableAd(Advert):
    pass
