import sae

from cmstodo import wsgi


application = sae.create_wsgi_app(wsgi.application)
