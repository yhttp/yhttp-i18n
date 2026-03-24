import functools


class Translator:
    def gettext(self, s):
        return s


class I18n:
    def configure(self, settings):
        self.settings = settings

    def __call__(self, handler):

        @functools.wraps(handler)
        def wrapper(req, *a, **kw):
            req.translator = Translator()
            return handler(req, *a, **kw)

        return wrapper
