from .cli import I18nCLI
from .i18n import I18n


DEFAULT_SETTINGS = '''
directory: i18n
default: en-US
'''


def install(app):
    app.cliarguments.append(I18nCLI)
    app.settings.merge('i18n: {}')
    app.settings.i18n.merge(DEFAULT_SETTINGS)
    app.i18n = I18n()

    @app.when
    def ready(app):
        app.i18n.configure(app.settings.i18n)
