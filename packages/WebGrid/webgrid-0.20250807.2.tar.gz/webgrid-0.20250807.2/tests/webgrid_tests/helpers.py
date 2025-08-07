from pathlib import Path

from blazeutils.testing import assert_equal_txt
import flask
from flask_webtest import SessionScope
import sqlalchemy as sa
from werkzeug.datastructures import MultiDict
import wrapt

from webgrid import Column
from webgrid_ta.model import db


cdir = Path(__file__).parent

db_sess_scope = SessionScope(db)


class ModelBase:
    @classmethod
    def setup_class(cls):
        db_sess_scope.push()

    @classmethod
    def teardown_class(cls):
        db_sess_scope.pop()


def eq_html(html, filename):
    with cdir.joinpath('data', filename).open('rb') as fh:
        file_html = fh.read().decode('ascii')
    assert_equal_txt(html, file_html)


def _inrequest(*req_args, **req_kwargs):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        with flask.current_app.test_request_context(*req_args, **req_kwargs):
            # replaces request.args wth MultiDict so it is mutable
            flask.request.args = MultiDict(flask.request.args)
            return wrapped(*args, **kwargs)

    return wrapper


def render_in_grid(grid_cls, render_in):
    """Class factory which extends an existing grid class
    to add a column that is rendered everywhere except "render_in"
    """
    other_render_types = set(Column._render_in)
    other_render_types.remove(render_in)

    class RenderInGrid(grid_cls):
        Column('Exclude', sa.literal('Exclude'), render_in=tuple(other_render_types))

    return RenderInGrid
