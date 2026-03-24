from .i18n import I18n


DEFAULT_SETTINGS = '''
domain: messages
directory: i18n
'''


def install(app):
    app.settings.merge('i18n: {}')
    app.settings.i18n.merge(DEFAULT_SETTINGS)
    app.i18n = I18n()

    @app.when
    def ready(app):
        app.i18n.configure(app.settings.i18n)
