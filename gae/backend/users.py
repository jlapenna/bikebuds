# Module supporting storing user info.

from google.appengine.ext import ndb


class User(ndb.Model):
    """Holds user info."""
    name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get(cls, claims):
        return User.get_or_insert(claims['sub'])

    @classmethod
    def get_key(cls, claims):
        return ndb.Key(User, claims['sub'])
