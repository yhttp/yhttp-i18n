import os

from bddrest import status, response, when
from yhttp.core import json

from yhttp.ext.i18n import install


def test_extension(httpreq, app, tmpdir):
    install(app)
    i18ndirectory = os.path.join(tmpdir, 'i18n')
    app.settings.i18n.directory = i18ndirectory
    app.ready()

    assert app.settings.i18n.directory == i18ndirectory

    @app.route()
    @json
    def get(req):
        return dict(
            message=req.translator.gettext('foo'),
            rtl=req.locale.rtl
        )

    with httpreq():
        assert status == 200
        assert response == dict(
            message='foo',
            rtl=False
        )

        when(headers={'accept-languages': 'fa-IR'})
        assert status == 200
        assert response == dict(
            message='foo',
            rtl=True
        )
