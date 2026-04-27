import re
import gettext
from urllib.parse import unquote

from .locale import Locale


def middleware(req):
    settings = req.application.settings.i18n
    req.translator = gettext.translation(
        domain=settings.domain,
        localedir=settings.localedirectory,
        languages=req.locales,
        fallback=True,
    )

    try:
        req.locale = Locale.parse(req.locales[0])
    except ValueError:
        req.locale = Locale.parse(settings.defaultlocale)


class PathRewriterMiddleware:
    def __init__(self, languages: dict[str, str],
                 pattern=r'^/([a-z]{2})(/.*)?'):
        self._pattern = re.compile(pattern)
        self._languages = languages

    def __call__(self, req):
        match_ = self._pattern.match(req.path)

        if not match_:
            return

        lang = match_.group(1)
        if lang not in self._languages:
            return

        req.locales = [self._languages[lang]]
        if len(req.path) == 3:
            req.path += '/'

        req.path = req.path[3:]
