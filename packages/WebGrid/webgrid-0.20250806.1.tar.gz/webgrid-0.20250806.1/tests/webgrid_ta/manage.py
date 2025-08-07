import logging
import urllib

import click
import flask

from webgrid_ta.app import create_app
from webgrid_ta.extensions import lazy_gettext as _
import webgrid_ta.model as model
from webgrid_ta.model.helpers import clear_db


log = logging.getLogger(__name__)

app = None


@click.group()
def main():
    """Run the Webgrid Test App CLI."""
    app = create_app('Dev')
    flask.ctx.AppContext(app).push()


@main.command('create-db')
@click.option('--clear', default=False, is_flag=True, help=_('DROP all DB objects first'))
def database_init(clear):
    if clear:
        clear_db()
        print(_('- db cleared'))

    model.load_db()
    print(_('- db loaded'))


@main.command('list-routes')
def list_routes():
    output = []
    for rule in flask.current_app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f'{rule.endpoint:50s} {methods:20s} {rule}')
        output.append(line)

    for line in sorted(output):
        print(line)


main.add_command(flask.cli.run_command)


@main.command('verify-translations')
def verify_translations():
    from pathlib import Path

    from morphi.messages.validation import check_translations

    root_path = Path(__file__).resolve().parent.parent.parent
    check_translations(
        root_path,
        'webgrid',
    )


if __name__ == '__main__':
    main()
