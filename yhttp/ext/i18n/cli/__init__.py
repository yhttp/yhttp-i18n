from easycli import SubCommand

from .extract import ExtractCommand
from .init import InitCommand
from .update import UpdateCommand
from .compile import CompileCommand


class I18nCLI(SubCommand):
    __command__ = 'i18n'
    __arguments__ = [
        ExtractCommand,
        InitCommand,
        UpdateCommand,
        CompileCommand,
    ]
