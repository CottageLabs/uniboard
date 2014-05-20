from portality.authorise import Authorise
from portality import dao
from portality.core import app
import uuid
from datetime import datetime, timedelta

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

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
    # FIXME: this method needs to be re-written as part of the user registration work
    # we are not having usernames (people are identified by email address), so we either
    # want to use their email address as their id, or mint them an opaque id.
    @classmethod
    def make_account(cls, username, name=None, email=None, degree=None, postcode=None, phone=None, graduation=None, roles=[]):
        a = cls.pull(username)
        if a:
            return a

        a = Account(id=email)
        a.set_name(name) if name else None
        #a.set_email(email) if email else None
        a.set_degree(degree) if degree else None
        a.set_location(lat,lon) if postcode else None
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
        return check_password_hash(self.data['password'], password)

    @property
    def degree(self):
        return self.data.get("degree")

    def set_degree(self, val):
        self.data["degree"] = val

    @property
    def postcode(self):
        return self.data.get("postcode")

    def set_postcode(self, val):
        self.data["postcode"] = val

    @property
    def location(self):
        loc = self.data.get("loc")
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

    @property
    def phone(self):
        return self.data.get("phone")

    def set_phone(self, val):
        self.data["phone"] = val

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

    def is_deleted(self):
        return self.data.get("admin", {}).get("deleted", False)

    def set_deleted(self, val):
        if type(val) != bool:
            raise ModelException("Unable to set deleted - must be boolean value")
        if "admin" not in self.data:
            self.data["admin"] = {}
        self.data["admin"]["deleted"] = val

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

    @classmethod
    def get_by_activation_token(cls, activation_token, not_expired=True):
        res = cls.query(q='activation_token.exact:"' + activation_token + '"')
        obs = [hit.get("_source") for hit in res.get("hits", {}).get("hits", [])]
        if len(obs) == 0 or len(obs) > 1:
            return None
        expires = obs[0].get("activation_expires")
        if expires is None:
            return None
        if not_expired:
            try:
                ed = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%SZ")
                if ed < datetime.now():
                    return None
            except:
                return None
        return cls(**obs[0])
    
    @property
    def is_super(self):
        # return not self.is_anonymous() and self.id in app.config['SUPER_USER']
        return Authorise.has_role(app.config["SUPER_USER_ROLE"], self.data.get("role", []))
    
    def has_role(self, role):
        return Authorise.has_role(role, self.data.get("role", []))
    
    def add_role(self, role):
        if "role" not in self.data:
            self.data["role"] = []
        self.data["role"].append(role)
    
    @property
    def role(self):
        return self.data.get("role", [])
    
    def set_role(self, role):
        if not isinstance(role, list):
            role = [role]
        self.data["role"] = role


