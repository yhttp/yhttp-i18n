from .cli import I18nCLI
from .decorator import create_i18n_decorator


DEFAULT_SETTINGS = '''
domain: messages
localedirectory: i18n
'''


def install(app):
    app.cliarguments.append(I18nCLI)
    app.settings.merge('i18n: {}')
    app.settings.i18n.merge(DEFAULT_SETTINGS)
    app.i18n = create_i18n_decorator(app.settings.i18n)
