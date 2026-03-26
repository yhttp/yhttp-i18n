import os
import datetime

from babel.messages.pofile import write_po, read_po
from babel.util import LOCALTZ

from easycli import SubCommand, Argument


class InitCommand(SubCommand):
    __command__ = 'init'
    __aliases__ = ['i']
    __arguments__ = [
        Argument(
            'locale',
            metavar='LOCALE',
            help='Locale to initialize a *.po file for it'
        ),
        Argument(
            '--locale-directory',
            metavar='DIRECTORY',
            help='Output locale catalog directory, default is the value '
                 'specified in the Application settings key: '
                 'i18n.localedirectory.'
        ),
        Argument(
            '--domain',
            metavar='DOMAIN',
            help='Translation domain, default is the value specified in the '
                 'Application settings key: i18n.domain.'
        ),
    ]

    def _init_catalog(self, infile, outfile, locale, width):
        with open(infile, 'rb') as infile:
            catalog = read_po(infile, locale=locale)

        catalog.locale = locale
        catalog.revision_date = datetime.datetime.now(LOCALTZ)
        catalog.fuzzy = False

        if dirname := os.path.dirname(outfile):
            os.makedirs(dirname, exist_ok=True)

        with open(outfile, 'wb') as outfile:
            write_po(outfile, catalog, width=width)

    def __call__(self, args):
        app = args.application
        app.ready()
        settings = app.settings.i18n
        domain = args.domain if args.domain else settings.domain
        localedir = args.locale_directory \
            if args.locale_directory \
            else settings.localedirectory

        infile = f'{localedir}/{domain}.pot'
        outfile = f'{localedir}/{args.locale}/LC_MESSAGES/{domain}.po'

        print(f'Creating catalog {outfile} based on {infile}')
        self._init_catalog(infile, outfile, args.locale, 79)
