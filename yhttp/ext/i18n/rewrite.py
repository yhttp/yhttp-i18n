import re
from urllib.parse import unquote


def create_rewriter(langs: dict[str, str], pattern=r'^/([a-z]{2})(/.*)?'):
    _langpat = re.compile(pattern)

    def rewrite(environ):
        path_ = unquote(environ['PATH_INFO'])
        match_ = _langpat.match(path_)

        if match_:
            lang = match_.group(1)
            if lang in langs:
                environ['HTTP_ACCEPT_LANGUAGES'] = langs[lang]
                if len(path_) == 3:
                    path_ += '/'
                environ['PATH_INFO'] = path_[3:]

    return rewrite
