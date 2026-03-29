import functools
import gettext

from .locale import Locale


def create_i18n_decorator(settings):
    def gettranslator(req):
        return gettext.translation(
            domain=settings.domain,
            localedir=settings.localedirectory,
            languages=req.locales,
            fallback=True,
        )

    def decorator(handler):
        @functools.wraps(handler)
        def wrapper(req, *a, **kw):
            req.translator = gettranslator(req)
            try:
                req.locale = Locale.parse(req.locales[0])
            except ValueError:
                req.locale = Locale('en', 'US')

            return handler(req, *a, **kw)

        return wrapper

    return decorator
