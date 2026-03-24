import os
import io
import uuid

from bddrest import status

from yhttp.ext.i18n import install


def test_extension(httpreq, app, tempdir, mocker):
    install(app)
    i18ndirectory = os.path.join(tempdir, 'i18n')
    app.settings.i18n.directory = i18ndirectory
    app.ready()

    assert app.i18n
    assert app.i18n.settings.physical == i18ndirectory

    @app.route()
    def get(req):
        app.i18n.get_translation(req.locales)

    # mockuuid = '3301a833-f9c8-49d9-ac43-df96f6798e55'
    # expected_filename = f'{mockuuid}.pdf'
    # mocker.patch.object(uuid, 'uuid4', return_value=uuid.UUID(mockuuid))
    # file = io.BytesIO(b'foobarbaz')
    # file.name = 'foo.pdf'
    # with httpreq(verb='POST', multipart=dict(foo=file)):
    #     assert status == 200

    # with httpreq(verb='DELETE', form=dict(filename=expected_filename)):
    #     assert status == 200

    #     assert not os.path.exists(expected)
