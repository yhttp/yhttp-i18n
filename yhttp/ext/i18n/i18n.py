import functools
import gettext


class I18n:
    def configure(self, settings):
        self.settings = settings

    def gettranslator(self, req):
        return gettext.translation(
            domain=self.settings.domain,
            localedir=self.settings.directory,
            languages=req.locales,
            fallback=True,
        )

    def __call__(self, handler):
        @functools.wraps(handler)
        def wrapper(req, *a, **kw):
            req.translator = self.gettranslator(req)
            return handler(req, *a, **kw)

        return wrapper
