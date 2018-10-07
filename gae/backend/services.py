# Module supporting storing service info.

from google.appengine.ext import ndb

import users


class Service(ndb.Model):
    """Holds service info."""
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get(cls, user_key, name):
        service_key = Service.get_key(user_key, name)
        service = service_key.get()
        modified = False
        if service is None:
            modified = True
            service = Service(key=service_key)
        if modified:
            service.put()
        return service

    @classmethod
    def get_key(cls, user_key, name):
        return ndb.Key(Service, name, parent=user_key)


class ServiceCredentials(ndb.Expando):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def default(cls, user_key, service_name):
        service_key = Service.get_key(user_key, service_name)
        return ndb.Key(ServiceCredentials, 'default', parent=service_key).get()

    @classmethod
    def get_key(cls, service_key):
        return ndb.Key(ServiceCredentials, 'default', parent=service_key)

    @classmethod
    @ndb.transactional
    def update(cls, user_key, service_name, new_credentials):
        service_key = Service.get_key(user_key, service_name)
        service_creds_key = ServiceCredentials.get_key(service_key)
        service_creds = service_creds_key.get()
        modified = False
        if service_creds is None:
            modified = True
            service_creds = ServiceCredentials(key=service_creds_key)
        for k, v in new_credentials.iteritems():
            modified = True
            setattr(service_creds, k, v)
        if modified:
            service_creds.put()
        return service_creds
