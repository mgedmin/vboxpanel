import os
from pyramid.paster import get_app

here = os.path.dirname(__file__)
application = get_app(os.path.join(here, 'production.ini'), 'main')
