from pyramid.security import Everyone, Allow
from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config

from .models import DBSession

class Root(object):
    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, 'group:Authenticated', 'add-keywords'),
            (Allow, 'group:Administrators', 'manage-keywords')
        ]


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings, root_factory=Root)
    config.add_static_view(name='static', path='static',
                           cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('keyword_manage', '/manage')
    config.add_route('keyword_export', '/manage/export')
    config.add_route('keyword_add', '/add')
    config.scan()
    app = config.make_wsgi_app()
    return app

