from django.core.handlers.wsgi import WSGIHandler
import django
import os
import sys

path = '/business-ecosystem-charging-backend/src'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


class WSGIEnvironment(WSGIHandler):

    def __call__(self, environ, start_response):

        os.environ['PAYPAL_CLIENT_ID'] = environ['PAYPAL_CLIENT_ID']
        os.environ['PAYPAL_CLIENT_SECRET'] = environ['PAYPAL_CLIENT_SECRET']
        django.setup()
        return super(WSGIEnvironment, self).__call__(environ, start_response)

application = WSGIEnvironment()
