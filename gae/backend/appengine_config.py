# Configures the backend to use vendored libraries
# https://cloud.google.com/appengine/docs/standard/python/tools/using-libraries-python-27#vendoring

from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')
