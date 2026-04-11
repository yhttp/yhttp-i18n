from bddrest import status, response, when, given
from yhttp.core import json

from yhttp.ext.i18n import Rewriter, install


def test_langrewriteapp(app, httpreq):
    install(app, rewriter=Rewriter(dict(
        en='en-US',
        fa='fa-IR',
    )))

    @app.route(r'/es/foo')
    @json
    def get(req):
        return 'Special Foo'

    @app.route(r'/(.*)?')
    @json
    def get(req, arg):
        return dict(locales=req.locales, arg=arg)

    with httpreq(path='/lang: en/foo'):
        assert status == 200
        assert response.json == dict(locales=['en-US'], arg='foo')

        when(path_parameters=given | dict(lang='fa'))
        assert status == 200
        assert response.json == dict(locales=['fa-IR'], arg='foo')

        when(path_parameters=given | dict(lang='ar'))
        assert status == 200
        assert response.json == dict(locales=['*'], arg='ar/foo')

        when(path_parameters=given | dict(lang='es'))
        assert status == 200
        assert response.json == 'Special Foo'

        when(path='/fa')
        assert status == 200
        assert response.json == dict(locales=['fa-IR'], arg='')

        when(path='/foo')
        assert status == 200
        assert response.json == dict(locales=['*'], arg='foo')

        when(path='/')
        assert status == 200
        assert response.json == dict(locales=['*'], arg='')
