import os
import sys
import tempfile

from babel.messages.pofile import write_po, read_po

from easycli import SubCommand, Argument


class UpdateCommand(SubCommand):
    __command__ = 'update'
    __aliases__ = ['u']
    __arguments__ = [
        Argument(
            'locale',
            metavar='LOCALE',
            nargs='?',
            help='Locale to update a *.po file for it, if not given all '
                 'available locales will be updated'
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

    def _update_catalog(self, domain, localedir, locales, infile, width):
        with open(infile, 'rb') as f:
            template = read_po(f)

        for locale in locales:
            outfile = os.path.join(localedir, locale, 'LC_MESSAGES',
                                   f'{domain}.po')
            print(f'Updating catalog {outfile} based on {infile}')

            if not os.path.exists(outfile):
                print(f'Catalog {outfile} not exists, init first',
                      file=sys.stderr)
                raise FileNotFoundError(outfile)

            with open(outfile, 'rb') as f:
                catalog = read_po(f, locale=locale, domain=domain)

            catalog.update(
                template,
                no_fuzzy_matching=True,
                update_header_comment=True,
                update_creation_date=True,
            )

            tmpname = os.path.join(
                os.path.dirname(outfile),
                tempfile.gettempprefix() + os.path.basename(outfile),
            )

            with open(tmpname, 'wb') as tmpfile:
                write_po(
                    tmpfile,
                    catalog,
                    ignore_obsolete=True,
                    include_previous=False,
                    omit_header=False,
                    width=width,
                )

            os.rename(tmpname, outfile)

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

        infile = f'{localedir}/{domain}.pot'
        locales = [args.locale] if args.locale \
            else list(self._getlocales(localedir))

        try:
            self._update_catalog(domain, localedir, locales, infile, 79)
        except FileNotFoundError:
            return 1
