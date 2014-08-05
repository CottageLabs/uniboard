import esprit
from portality.core import app
from datetime import datetime, timedelta

class AccountDAO(esprit.dao.DomainObject):
    __type__ = 'account'
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])

    @classmethod
    def pull_by_email(cls, email):
        res = cls.query(q='email:"' + email + '"')
        if res.get('hits',{}).get('total',0) == 1:
            return cls(res['hits']['hits'][0]['_source'])
        else:
            return None
    
    @classmethod
    def get_by_reset_token(cls, reset_token, not_expired=True):
        res = cls.query(q='reset_token.exact:"' + reset_token + '"')
        obs = [hit.get("_source") for hit in res.get("hits", {}).get("hits", [])]
        if len(obs) == 0 or len(obs) > 1:
            return None
        expires = obs[0].get("reset_expires")
        if expires is None:
            return None
        if not_expired:
            try:
                ed = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%SZ")
                if ed < datetime.now():
                    return None
            except:
                return None
        return cls(obs[0])

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
        return cls(obs[0])

    @classmethod
    def prefix_query(cls, field, prefix, size=5):
        # example of a prefix query
        # {
        #     "query": {"prefix" : { "bibjson.publisher" : "ope" } },
        #     "size": 0,
        #     "facets" : {
        #       "publisher" : { "terms" : {"field" : "bibjson.publisher.exact", "size": 5} }
        #     }
        # }
        if field.endswith(app.config['FACET_FIELD']):
            # strip .exact (or whatever it's configured as) off the end
            query_field = field[:field.rfind(app.config['FACET_FIELD'])]
        else:
            query_field = field

        # the actual terms should come from the .exact version of the
        # field - we are suggesting whole values, not fragments
        facet_field = query_field + app.config['FACET_FIELD']

        q = {
            "query": {"prefix" : { query_field : prefix } },
            "size": 0,
            "facets" : {
              field : { "terms" : {"field" : facet_field, "size": size} }
            }
        }

        r = esprit.raw.search(cls.__conn__, cls.__type__, q)
        return r.json()

    @classmethod
    def autocomplete(cls, field, prefix, size=5):
        res = cls.prefix_query(field, prefix, size=size)
        result = []
        for term in res['facets'][field]['terms']:
            # keep ordering - it's by count by default, so most frequent
            # terms will now go to the front of the result list
            result.append({"id": term['term'], "text": term['term']})
        return result

class AdvertDAO(esprit.dao.DomainObject):
    __type__ = 'advert'
    __conn__ = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_DB'])

    @classmethod
    def get_by_reactivate_token(cls, reactivate_token, not_expired=True):
        res = cls.query(q='admin.reactivate_token.exact:"' + reactivate_token + '"')
        obs = [hit.get("_source") for hit in res.get("hits", {}).get("hits", [])]
        if len(obs) == 0 or len(obs) > 1:
            return None
        expires = obs[0].get("reactivate_expires")
        if expires is None:
            return None
        if not_expired:
            try:
                ed = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%SZ")
                if ed < datetime.now():
                    return None
            except:
                return None
        return cls(obs[0])

    @classmethod
    def get_by_owner(cls, owner_id):
        query = {
            "query" : {
                "term" : {"owner.exact" : owner_id}
            },
            "sort" : [{"last_updated" : {"order" : "desc"}}],
        }
        return cls.iterate(query)

        """
        res = cls.query(terms={"owner.exact": [owner_id]}, size=1000)
        if 'hits' not in res:
            return []
        if res['hits']['total'] <= 0:
            return []

        hits = res['hits']['hits']
        results = [cls(raw=h['_source']) for h in hits]
        return results
        """

    @classmethod
    def prefix_query(cls, field, prefix, size=5):
        # example of a prefix query
        # {
        #     "query": {"prefix" : { "bibjson.publisher" : "ope" } },
        #     "size": 0,
        #     "facets" : {
        #       "publisher" : { "terms" : {"field" : "bibjson.publisher.exact", "size": 5} }
        #     }
        # }
        if field.endswith(app.config['FACET_FIELD']):
            # strip .exact (or whatever it's configured as) off the end
            query_field = field[:field.rfind(app.config['FACET_FIELD'])]
        else:
            query_field = field

        # the actual terms should come from the .exact version of the
        # field - we are suggesting whole values, not fragments
        facet_field = query_field + app.config['FACET_FIELD']

        q = {
            "query": {"prefix" : { query_field : prefix } },
            "size": 0,
            "facets" : {
              field : { "terms" : {"field" : facet_field, "size": size} }
            }
        }

        r = esprit.raw.search(cls.__conn__, cls.__type__, q)
        return r.json()

    @classmethod
    def autocomplete(cls, field, prefix, size=5):
        res = cls.prefix_query(field, prefix, size=size)
        result = []
        for term in res['facets'][field]['terms']:
            # keep ordering - it's by count by default, so most frequent
            # terms will now go to the front of the result list
            result.append({"id": term['term'], "text": term['term']})
        return result

    @classmethod
    def get_by_expiration(cls):
        res = []
        exp_time = (datetime.now() + timedelta(hours=36)).isoformat() + 'Z'
        query = {"query": {"range": {"admin.expires": {"lte": exp_time}}}}
        return cls.iterate(query)
