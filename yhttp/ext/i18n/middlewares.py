import re
import gettext

from yhttp.core import statuses

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
    def __init__(self, languages: dict[str, str], defaultlanguage=None,
                 pattern=r'^/([a-z]{2})(?:$|/.*)',
                 ignore=r'^/(apiv\d+|assets|media)'):
        self._pattern = re.compile(pattern)
        self._languages = languages
        self._ignore = re.compile(ignore)
        self._defaultlanguage = defaultlanguage

    def configure(self, settings):
        if not self._defaultlanguage:
            self._defaultlanguage = settings.defaultlocale.split('-', 1)[0]

    def __call__(self, req):
        reqpath = req.path
        if self._ignore.match(reqpath):
            return

        match_ = self._pattern.match(reqpath)

        if not match_:
            lang = req.locales[0]
            if lang == '*':
                lang = self._defaultlanguage

            raise statuses.found(f'/{lang}{req.fullpath.rstrip("/")}')

        lang = match_.group(1)
        if lang not in self._languages:
            return

        req.locales = [self._languages[lang]]
        if len(reqpath) == 3:
            reqpath += '/'

        req.originalpath = reqpath
        req.path = reqpath[3:]
