import re
from urllib.parse import unquote

from yhttp.core import BaseApplication


class LangRewriteApplication(BaseApplication):
    _langpat = re.compile(r'/([a-z]{2})/')

    def __init__(self, version, name, backend):
        self.backend = backend
        super().__init__(version, name)

    def __call__(self, environ, startresponse):
        path_ = unquote(environ['PATH_INFO'])
        match_ = self._langpat.match(path_)

        if match_:
            lang = match_.group(1)
            if lang in self.settings.languages:
                environ['HTTP_ACCEPT_LANGUAGES'] = \
                    self.settings.languages[lang]
                environ['PATH_INFO'] = path_[3:]

        # just pass the request to the super application
        return self.backend(environ, startresponse)

    def ready(self):
        super().ready()
        self.backend.ready()

    def shutdown(self):
        self.backend.shutdown()
        super().shutdown()

    def climain(self, argv=None):
        return self.backend.climain(argv)
