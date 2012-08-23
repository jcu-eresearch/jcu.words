from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('keyword_delete', '/delete')
    config.add_route('keyword_delete_one', '/delete/{keyword_id:\d+}')
    config.add_route('keyword_add', '/add')
    config.scan()
    return config.make_wsgi_app()

