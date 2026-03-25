from easycli import SubCommand

from .extract import ExtractCommand
from .init import InitCommand


class I18nCLI(SubCommand):
    __command__ = 'i18n'
    __arguments__ = [
        ExtractCommand,
        InitCommand,
    ]
