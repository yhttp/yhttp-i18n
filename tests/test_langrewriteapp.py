import functools

from bddcli import Given as CLIGiven, Application as CLIApplication, \
    status as clistatus, stderr, stdout
from bddrest import status, response, Given, when, given
from yhttp.core import Application, json

from yhttp.ext.i18n import LangRewriteApplication


_app = Application('0.1.0', 'foo')
_lrapp = LangRewriteApplication('0.1.0', 'foo', _app)


def test_langrewriteapp_cli(app):
    _lrapp.ready()
    cliapp = CLIApplication('foo', f'{__name__}:_lrapp.climain')

    with CLIGiven(cliapp, '--help'):
        print(stderr)
        print(stdout)
        assert clistatus == 0
        assert stderr == ''


def test_langrewriteapp(app):
    lrapp = LangRewriteApplication('0.1.0', 'foo', app)
    lrapp.settings.merge('''
      languages:
        en: en-US
        fa: fa-IR
    ''')

    lrapp.ready()
    httpreq = functools.partial(Given, lrapp)

    @app.route(r'/es/foo')
    @json
    def get(req):
        return 'Special Foo'

    @app.route(r'/foo')
    @json
    def get(req):
        return req.locales

    with httpreq(path='/lang: en/foo'):
        assert status == 200
        assert response.json == ['en-US']

        when(path_parameters=given | dict(lang='fa'))
        assert status == 200
        assert response.json == ['fa-IR']

        when(path_parameters=given | dict(lang='ar'))
        assert status == 404

        when(path_parameters=given | dict(lang='es'))
        assert status == 200
        assert response.json == 'Special Foo'

    _lrapp.shutdown()
