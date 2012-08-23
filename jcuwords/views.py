import colander
from beaker import cache
from pyramid_deform import FormView
from pyramid.response import Response
from pyramid.view import view_config, render_view
from pyramid.httpexceptions import HTTPFound
from pytagcloud import create_tag_image, make_tags, create_html_data
from pytagcloud.lang.counter import get_tag_counts

from jcuwords import models, config

class Keyword(colander.SequenceSchema):
    keyword = colander.SchemaNode(colander.String())

class AddKeywordsSchema(colander.MappingSchema):
    keywords = Keyword()

class KeywordManager(object):

    cls = models.Keyword

    def add(self, **kw):
        """Create and add object to database. Accepts all args that cls does.
        """
        obj = self.cls(**kw)
        models.DBSession.add(obj)

    def delete(self, identifier):
        query = models.DBSession.query(self.cls)
        obj = query.filter(self.cls.id == identifier).one()
        models.DBSession.delete(obj)

    def all(self):
        return models.DBSession.query(self.cls).all()


@view_config(name="keyword-cloud", renderer='templates/cloud.pt')
def keyword_cloud(context, request):
    return make_cloud()
 
@cache.cache_region('long_term')
def make_cloud():
     keywords = KeywordManager().all()
     text = ' '.join([kw.keyword for kw in keywords])
     tags = make_tags(get_tag_counts(text)[:30], minsize=2, maxsize=42)
     result = create_html_data(tags, size=(1000, 300))
     return result

@view_config(route_name='home', renderer='templates/home.pt')
class KeywordCloudView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if 'clear' in self.request.GET:
            cache.region_invalidate(make_cloud, None)
        return {'keyword_cloud': render_view(self.context,
                                             self.request,
                                             'keyword-cloud'),
                'return_url': config.RETURN_URL,
               }
    
class KeywordsFormView(FormView):

    buttons = ('submit', 'cancel')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        super(KeywordsFormView, self).__init__(request)

    def __call__(self):
        base = super(KeywordsFormView, self).__call__()
        if hasattr(base, 'update'):
            base.update({
                'return_url': config.RETURN_URL,
                })
        return base

    def cancel_success(self, appstruct):
        return HTTPFound(location=config.RETURN_URL)

    def submit_success(self, appstruct): 
        return HTTPFound(location=self.request.path_url)


@view_config(route_name='keyword_add', renderer='templates/form.pt')
class AddKeywordsFormView(KeywordsFormView):

    schema = AddKeywordsSchema()
    
    def submit_success(self, appstruct):
        for value in appstruct['keywords']:
            KeywordManager().add(**{'keyword': value, 'user_id': 'david'})
        response = super(AddKeywordsFormView, self).submit_success(appstruct) 
        return response

@view_config(route_name='keyword_delete_one')
@view_config(route_name='keyword_delete', renderer='templates/delete.pt')
class DeleteKeywordsFormView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if 'keyword_delete_one' == self.request.route_name:
            kw_id = int(self.request.matchdict['keyword_id'])
            KeywordManager().delete(kw_id)
            return HTTPFound(location=self.request.path_url)
            
        return {'keywords': KeywordManager().all(),
                'return_url': config.RETURN_URL,
               }

#class KeywordsAdminView(object):
#
#    add_form = AddKeywordsForm
#    delete_form = DeleteKeywordsForm

