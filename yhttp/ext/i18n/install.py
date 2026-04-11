import gettext
import functools

from .locale import Locale
from .cli import I18nCLI


DEFAULT_SETTINGS = '''
domain: messages
localedirectory: i18n
'''


def middleware(request_factory, rewriter=None):

    @functools.wraps(request_factory)
    def factory(app, environ, response):
        if rewriter:
            rewriter.rewrite(environ)

        req = request_factory(app, environ, response)
        settings = app.settings.i18n
        req.translator = gettext.translation(
            domain=settings.domain,
            localedir=settings.localedirectory,
            languages=req.locales,
            fallback=True,
        )

        try:
            req.locale = Locale.parse(req.locales[0])
        except ValueError:
            req.locale = Locale('en', 'US')

        return req

    return factory


def install(app, rewriter=None):
    app.cliarguments.append(I18nCLI)
    app.settings.merge('i18n: {}')
    app.settings.i18n.merge(DEFAULT_SETTINGS)
    app.request_factory = middleware(app.request_factory, rewriter)
