from bddrest import status, response, when, given
from yhttp.core import json, Request

from yhttp.ext.i18n import create_rewriter


def test_langrewriteapp(app, httpreq):
    rewrite = create_rewriter(dict(
        en='en-US',
        fa='fa-IR',
    ))

    def create_request(app, environ, response):
        rewrite(environ)
        return Request(app, environ, response)

    app.request_factory = create_request

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
