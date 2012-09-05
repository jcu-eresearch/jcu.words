import csv
from StringIO import StringIO

import deform
from beaker import cache
import bleach

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.i18n import Localizer
from pyramid.path import AssetResolver
from pyramid.response import Response
from pyramid.security import has_permission, authenticated_userid
from pyramid.view import view_config, view_defaults, render_view

from pyramid_deform import FormView
from pytagcloud import create_tag_image, make_tags, create_html_data, \
        LAYOUT_HORIZONTAL, LAYOUT_MIX
from pytagcloud.lang.counter import get_tag_counts

from js.jquery import jquery
import css.css3githubbuttons

import jcu.common
from jcuwords import models, schemas, resources


class KeywordManager(object):

    cls = models.Keyword

    def __init__(self, session=models.DBSession):
        self.session = session

    def add(self, **kw):
        """Create and add object to database. Accepts all args that cls does.
        """
        obj = self.cls(**kw)
        self.session.add(obj)

    def delete(self, identifier):
        """Delete the given database entry associated with ``identifier``.
        """
        query = self.session.query(self.cls)
        obj = query.filter(self.cls.id == identifier).one()
        self.session.delete(obj)

    def all(self, order_by=None):
        """Return all database entries.
        """
        order_by = order_by and getattr(self.cls, order_by, None) or None
        return self.session.query(self.cls).order_by(order_by).all()

    def has_any(self, **kw):
        """Return True if any database entries are attached to the query.
        """
        query = self.session.query(self.cls)
        for key, value in kw.items():
            expr = getattr(self.cls, key) == value
            query = query.filter(expr)
        return bool(query.all())


@view_defaults(renderer='templates/cloud.pt')
class CloudMaker(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.resolver = AssetResolver()

    @view_config(name="keyword-cloud.png")
    def keyword_cloud_png(self):
        asset = self.resolver.resolve('jcuwords:keyword-cloud.png')
        _cloud = open(asset.abspath()).read()
        return Response(content_type='text/png',
                        body=_cloud)

    @view_config(name="keyword-cloud")
    def keyword_cloud(self):
        return self.make_cloud(True)

    @view_config(name="keyword-cloud-image")
    def keyword_cloud_image(self):
        image_url = self.request.resource_url(None, 'keyword-cloud.png')
        return {'image': image_url}

    def invalidate(self):
        cache.region_invalidate(self.make_cloud, None, False)
        cache.region_invalidate(self.make_cloud, None, True)

    def make_cloud(self, output_html):
        keywords = KeywordManager().all()
        text = ' '.join([kw.keyword for kw in keywords])

        if output_html:
            max_tags = 30
            max_size = 42
        else:
            max_tags = 100
            max_size = 60

        tags = make_tags(get_tag_counts(text)[:max_tags], minsize=1,
                         maxsize=max_size)

        if output_html:
            size = (900, 300)
            result = create_html_data(tags, size=size,
                                      layout=LAYOUT_HORIZONTAL)
        else:
            #now = datetime.utcnow()
            #filename = 'jcuwords/static/clouds/keyword-cloud-%s.png' % now.isoformat()
            cloud = self.resolver.resolve('jcuwords:keyword-cloud.png')
            filename = cloud.abspath()
            size = (1024, 500)
            create_tag_image(tags, filename, size=size,
                             fontname='IM Fell DW Pica',
                             layout=LAYOUT_MIX)
            image_url = self.request.resource_url(None, 'keyword-cloud.png')
            result = {'image': image_url}

        return result


class BaseView(object):
    """Base class for all views in the application."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        jquery.need()
        jcu.common.resources.alerts.need()
        css.css3githubbuttons.buttons.need()
        resources.css_resource.need()


@view_config(route_name='home', renderer='templates/home.pt')
class KeywordCloudView(BaseView):

    def __call__(self):
        super(KeywordCloudView, self).__call__()
        if 'clear' in self.request.GET:
            CloudMaker(self.context, self.request).make_cloud(False)
        return {'keyword_cloud': render_view(self.context,
                                             self.request,
                                             'keyword-cloud-image'),
               }


class KeywordsFormView(BaseView, FormView):

    buttons = (deform.Button('submit', klass='button'),)

    def __init__(self, context, request):
        BaseView.__init__(self, context, request)
        FormView.__init__(self, request)

    def __call__(self):
        BaseView.__call__(self)
        base = FormView.__call__(self)
        return base

    def submit_success(self, appstruct):
        return HTTPFound(location=self.request.path_url)


@view_config(route_name='keyword_add', renderer='templates/form.pt',
             permission='add-keywords')
class AddKeywordsFormView(KeywordsFormView):

    schema = schemas.AddKeywordsSchema()

    def __init__(self, context, request):
        super(AddKeywordsFormView, self).__init__(context, request)
        self.kw_manager = KeywordManager()
        self.user_id = authenticated_userid(request)

    def __call__(self):
        base = {}
        can_manage = has_permission('manage-keywords',
                                    self.context,
                                    self.request)

        if can_manage or not self.kw_manager.has_any(user_id=self.user_id):
            base = super(AddKeywordsFormView, self).__call__()
            if isinstance(base, Response):
                return base
        else:
            base.update({'form': "You've already entered your keywords."
                                 " Thanks for your submission!",
                         'has_submitted': True})


        base.update(KeywordCloudView(self.context, self.request)())
        return base

    def submit_success(self, appstruct):
        manager = KeywordManager()
        for value in appstruct['keywords']:
            value = value.strip()
            if value:
                value_clean = bleach.clean(value)
                manager.add(**{'keyword': value_clean,
                               'user_id': self.user_id})
        response = super(AddKeywordsFormView, self).submit_success(appstruct)
        self.request.session.flash(('info', 'Thanks for your submission. Your words will appear in the keyword cloud shortly.'))
        return response


@view_defaults(permission='manage-keywords')
class ManageKeywordsView(BaseView):

    def __init__(self, context, request):
        super(ManageKeywordsView, self).__init__(context, request)
        self.manager = KeywordManager()

    @view_config(route_name='keyword_manage', renderer='templates/manage.pt')
    def manage_view(self):
        BaseView.__call__(self)
        
        if self.request.method == 'POST':
            #Check CSRF token
            if self.request.POST.get('csrf_token') != self.request.session.get_csrf_token():
                raise HTTPForbidden('Invalid cross-site scripting token')

            successes = 0
            for kw in self.request.POST.getall('keyword'):
                kw_id = int(kw)
                self.manager.delete(kw_id)
                successes += 1

            localizer = Localizer(None, None)
            message = localizer.pluralize(
                'Successfully deleted ${count} word',
                'Successfully deleted ${count} words',
                successes,
                mapping={'count': successes}
            )
            self.request.session.flash(('info', message))
            return HTTPFound(location=self.request.referrer)


        order_by = self.request.GET.get('sort')
        if order_by not in ['keyword', 'entered_on', 'user_id']:
            order_by = 'keyword'

        return {'keywords': self.manager.all(order_by=order_by)}

    @view_config(route_name='keyword_export', renderer='string')
    def export_view(self):
        output = StringIO()
        writer = csv.DictWriter(output,
                                ['id', 'keyword', 'entered_on', 'user_id'],
                                extrasaction='ignore')
        for keyword in self.manager.all():
            writer.writerow(vars(keyword))
        return output.getvalue()
