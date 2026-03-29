import babel
from yhttp.core import lazyattribute


RTL_LANGUAGES = [
    'fa',
    'ar',
    'he',
    'ps',
    'sd',
    'ur',
    'yi',
    'dv',
    'ha',
    'ks',
    'ku',
    'tk',
    'ug',
]


class Locale(babel.Locale):
    @lazyattribute
    def rtl(self):
        return self.language in RTL_LANGUAGES
