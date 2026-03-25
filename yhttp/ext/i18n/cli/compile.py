import os
import sys

from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo

from easycli import SubCommand, Argument


class CompileCommand(SubCommand):
    __command__ = 'compile'
    __aliases__ = ['c']
    __arguments__ = [
        Argument(
            'locale',
            metavar='LOCALE',
            nargs='?',
            help='Locale to compile a *.mo file for it, if not given all '
                 'available locales will be compiled'
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
        Argument(
            '--no-statistics',
            action='store_true',
            default=False,
            help='Print statistics about translations.'
        ),
    ]

    def _compile_catalog(self, domain, localedir, locales, args):
        errors = {}

        for locale in locales:
            outfile = os.path.join(localedir, locale, 'LC_MESSAGES',
                                   f'{domain}.mo')
            infile = os.path.join(localedir, locale, 'LC_MESSAGES',
                                  f'{domain}.po')

            if not os.path.exists(infile):
                print(f'Catalog {infile} not exists, init first',
                      file=sys.stderr)
                raise FileNotFoundError(infile)

            with open(infile, 'rb') as f:
                catalog = read_po(f, locale=locale, domain=domain)

            if not args.no_statistics:
                translated = 0
                for message in list(catalog)[1:]:
                    if message.string:
                        translated += 1

                percentage = 0
                if len(catalog):
                    percentage = translated * 100 // len(catalog)

                print(
                    f'{translated} of {len(catalog)} messages '
                    f'({percentage}%) translated in {infile}',
                )

            errors[catalog] = list(catalog.check())
            for message, errs in errors[catalog]:
                for error in errs:
                    print(f'error: {infile}:{message.lineno}: {error}')

            print(f'Compiling catalog {outfile} based on {infile}')
            with open(outfile, 'wb') as f:
                write_mo(f, catalog, use_fuzzy=False)

        return errors

    def _getlocales(self, localedir):
        for d in os.listdir(localedir):
            if not os.path.isdir(os.path.join(localedir, d)):
                continue

            yield d

    def __call__(self, args):
        app = args.application
        app.ready()
        settings = app.i18n.settings
        domain = args.domain if args.domain else settings.domain
        localedir = args.locale_directory \
            if args.locale_directory \
            else settings.localedirectory

        locales = [args.locale] if args.locale \
            else list(self._getlocales(localedir))

        try:
            errors = self._compile_catalog(domain, localedir, locales, args)
        except FileNotFoundError:
            return 1

        nerr = 0
        for e in errors.values():
            nerr += len(e)

        if nerr:
            print(f'{nerr} error(s) encountered.')
