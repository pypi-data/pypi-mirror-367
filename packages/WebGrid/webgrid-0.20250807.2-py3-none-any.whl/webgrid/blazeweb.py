from blazeweb.content import getcontent
from blazeweb.globals import ag, rg, user
from blazeweb.routing import abs_static_url
from blazeweb.templating.jinja import content_filter
from blazeweb.utils import abort
from blazeweb.wrappers import StreamResponse
from jinja2.exceptions import TemplateNotFound
from sqlalchemybwc import db as sabwc_db

from webgrid import BaseGrid
from webgrid.extensions import FrameworkManager, gettext
from webgrid.renderers import render_html_attributes


class WebGrid(FrameworkManager):
    def __init__(self, db=None, component='webgrid'):
        super().__init__(db=db or sabwc_db)
        self.component = component

    def init(self):
        ag.tplengine.env.filters['wg_safe'] = content_filter
        ag.tplengine.env.filters['wg_attributes'] = render_html_attributes
        ag.tplengine.env.filters['wg_gettext'] = gettext

    def sa_query(self, *args, **kwargs):
        return self.db.sess.query(*args, **kwargs)

    def request_form_args(self):
        """Return POST request args."""
        return rg.request.form

    def request_json(self):
        """Return json body of request."""
        return rg.request.json

    def request_url_args(self):
        """Return GET request args."""
        return rg.request.args

    def csrf_token(self):
        raise NotImplementedError

    def web_session(self):
        return user

    def persist_web_session(self):
        pass

    def flash_message(self, category, message):
        user.add_message(category, message)

    def request(self):
        return rg.request

    def static_url(self, url_tail):
        return abs_static_url(f'component/webgrid/{url_tail}')

    def file_as_response(self, data_stream, file_name, mime_type):
        rp = StreamResponse(data_stream)
        rp.headers['Content-Type'] = mime_type
        if file_name is not None:
            rp.headers['Content-Disposition'] = f'attachment; filename={file_name}'
        abort(rp)

    def render_template(self, endpoint, **kwargs):
        try:
            return getcontent(endpoint, **kwargs)
        except TemplateNotFound:
            if ':' in endpoint:
                raise
            return getcontent(f'{self.component}:{endpoint}', **kwargs)


wg_blaze_manager = WebGrid()


class Grid(BaseGrid):
    manager = wg_blaze_manager
