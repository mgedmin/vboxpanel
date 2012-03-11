import os
from pyramid.paster import get_app, setup_logging

here = os.path.dirname(__file__)
config_file = os.path.join(here, 'production.ini')
setup_logging(config_file + '#main') # the bit after # is actually irrelevant
application = get_app(config_file, 'main')
