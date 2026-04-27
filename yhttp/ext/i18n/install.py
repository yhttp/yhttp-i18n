from .cli import I18nCLI
from .middlewares import middleware


DEFAULT_SETTINGS = '''
domain: messages
defaultlocale: en_US
localedirectory: i18n
'''


def install(app, rewriter=None):
    app.cliarguments.append(I18nCLI)
    app.settings.merge('i18n: {}')
    app.settings.i18n.merge(DEFAULT_SETTINGS)

    if rewriter:
        app.middlewares.append(rewriter)

    app.middlewares.append(middleware)
