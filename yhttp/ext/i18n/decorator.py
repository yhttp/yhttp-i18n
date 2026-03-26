import functools
import gettext


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
            return handler(req, *a, **kw)

        return wrapper

    return decorator
