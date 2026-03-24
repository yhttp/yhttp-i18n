import os

from bddrest import status, response
from yhttp.core import text

from yhttp.ext.i18n import install


def test_extension(httpreq, app, tempdir):
    install(app)
    i18ndirectory = os.path.join(tempdir, 'i18n')
    app.settings.i18n.directory = i18ndirectory
    app.ready()

    assert app.i18n
    assert app.i18n.settings.directory == i18ndirectory

    @app.route()
    @app.i18n
    @text
    def get(req):
        return req.translator.gettext('foo')

    with httpreq():
        assert status == 200
        assert response == 'foo'
