import os

class ProdConfig(object):
    def __init__(self):
        self.backend_url = 'https://backend-dot-bikebuds-app.appspot.com'
        self.frontend_url = 'https://bikebuds.joelapenna.com'
        self.origins = [self.backend_url, self.frontend_url]


class LocalConfig(object):
    def __init__(self):
        self.backend_url = 'http://localhost:8081'
        self.frontend_url = 'http://localhost:8080'
        self.origins = [self.backend_url, self.frontend_url]


if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    config = ProdConfig()
else:
    config = LocalConfig()

