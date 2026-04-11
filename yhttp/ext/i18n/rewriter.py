import re
from urllib.parse import unquote


class Rewriter:
    def __init__(self, languages: dict[str, str],
                 pattern=r'^/([a-z]{2})(/.*)?'):
        self._pattern = re.compile(pattern)
        self._languages = languages

    def rewrite(self, environ):
        path_ = unquote(environ['PATH_INFO'])
        match_ = self._pattern.match(path_)

        if not match_:
            return

        lang = match_.group(1)
        if lang not in self._languages:
            return

        environ['HTTP_ACCEPT_LANGUAGES'] = self._languages[lang]
        if len(path_) == 3:
            path_ += '/'

        environ['PATH_INFO'] = path_[3:]
