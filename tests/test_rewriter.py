from bddrest import status, response, when, given
from yhttp.core import json

from yhttp.ext.i18n import PathRewriterMiddleware, install


def test_langrewriteapp(app, httpreq):
    install(app, rewriter=PathRewriterMiddleware(dict(
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

        when(path='/aa/')
        assert status == 200
        assert response.json == dict(locales=['*'], arg='aa/')

        when(path='/foo')
        assert status == 302
        assert response.headers['location'] == '/en/foo'

        when(path='/')
        assert status == 302
        assert response.headers['location'] == '/en'

        when(path='/foo/bar')
        assert status == 302
        assert response.headers['location'] == '/en/foo/bar'

        when(path='/apiv1')
        assert status == 200
        assert response.json == dict(locales=['*'], arg='apiv1')

        when(path='/apiv1/tokens')
        assert status == 200
        assert response.json == dict(locales=['*'], arg='apiv1/tokens')
