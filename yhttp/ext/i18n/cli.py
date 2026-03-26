import os
import sys
import fnmatch
import tempfile
import datetime

from easycli import SubCommand, Argument
from babel.messages.extract import extract_from_dir
from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po
from babel.messages.mofile import write_mo
from babel.util import LOCALTZ


CATALOG_HEADER = \
    '# Translations template for PROJECT.\n' \
    '# Copyright (C) YEAR ORGANIZATION\n'


class ExtractCommand(SubCommand):
    __command__ = 'extract'
    __aliases__ = ['e']
    __arguments__ = [
        Argument(
            'directories',
            nargs='*',
            metavar="SEARCH-PATHS",
            default=['.'],
            help='Source directories to search for messages'
        ),
        Argument(
            '--mako',
            action='store_true',
            help='Enable *.mako files extraction'
        ),
        Argument(
            '--locale-directory',
            metavar='DIRECTORY',
            help='Output locale catalog directory, default is the value '
                 'specified in the Application settings key: '
                 'i18n.localedirectory.'
        ),
        Argument(
            '--ignore-file',
            dest='ignore_files',
            metavar='PATTERN',
            default=[],
            action='append',
            help='Wildcard pattern to ignore files, this option can be'
                 ' specified multiple times.'
        ),
        Argument(
            '--ignore-directory',
            dest='ignore_directories',
            metavar='PATTERN',
            default=[],
            action='append',
            help='Wildcard pattern to ignore directories, this option can be'
                 ' specified multiple times.'
        ),
        Argument(
            '--domain',
            metavar='DOMAIN',
            help='Translation domain, default is the value specified in the '
                 'Application settings key: i18n.domain.'
        ),
        Argument(
            '--language-team',
            metavar='TEAM',
            help='Language team name.'
        ),
        Argument(
            '--copyright',
            metavar='COPYRIGHT',
            help='Copyright holder.'
        ),
        Argument(
            '--email',
            metavar='EMAIL',
            help='Email address to report bugs.'
        ),
        Argument(
            '-o',
            '--output-file',
            metavar='FILENAME',
            help='Output catalog to generate, default is the name specified in'
                 ' the `--domain` argument with the `.pot` exension within the'
                 ' directory specified by the `--locale-directory` argument.'
        )
    ]

    def _onfile(self, directory):
        def callback(fn, method, opts):
            if method == 'ignore':
                return

            filepath = os.path.normpath(os.path.join(directory, fn))
            optstr = ''
            if opts:
                opt_values = ", ".join(f'{k}="{v}"' for k, v in opts.items())
                optstr = f" ({opt_values})"

            print(f'Extracting messages from {filepath}{optstr}')

        return callback

    def _make_directoryfilter(self, patterns):
        """
        Build a directory_filter function based on a list of ignore patterns.
        """
        ignore_patterns = [
            '.*',
            '_*',
        ]
        ignore_patterns.extend(patterns)

        def filter(dirname):
            basename = os.path.basename(dirname)
            return not any(
                fnmatch.fnmatch(basename, p) for p in ignore_patterns
            )

        return filter

    def _extract(self, catalog, directory, method_map, options_map, ignore):
        print(f'Extracting messages from: {directory}')
        extracted = extract_from_dir(
            dirname=directory,
            method_map=method_map,
            options_map=options_map,
            keywords={
                '_': None,
                'N_': None,
                'P_': ((1, 'c'), 2),
                'NP_': ((1, 'c'), 2, 3),
                # 'dgettext': (2,),
                # 'dngettext': (2, 3),
                # 'dnpgettext': ((2, 'c'), 3, 4),
                # 'dpgettext': ((2, 'c'), 3),
                # 'gettext': None,
                # 'ngettext': (1, 2),
                # 'npgettext': ((1, 'c'), 2, 3),
                # 'pgettext': ((1, 'c'), 2),
                # 'ugettext': None,
                # 'ungettext': (1, 2)
            },
            comment_tags=['TRANSLATOR:', 'NOTE:'],
            callback=self._onfile(directory),
            strip_comment_tags=False,
            directory_filter=self._make_directoryfilter(ignore),
        )

        for filename, lineno, message, comments, context in extracted:
            filepath = os.path.normpath(os.path.join(directory, filename))

            catalog.add(
                message,
                None,
                [(filepath, lineno)],
                auto_comments=comments,
                context=context,
            )

    def __call__(self, args):
        app = args.application
        app.ready()
        settings = app.settings.i18n

        method_map = [
            ('**.py', 'python'),
        ]
        for i in args.ignore_files:
            method_map.append((i, 'ignore'))

        options_map = {}
        if args.mako:
            # ensure mako is installed already
            try:
                import mako  # noqa: F401
            except ImportError:
                print('Mako must be installed when using `--mako` flag',
                      file=sys.stderr)
                return -1

            method_map.append(('**.mako', 'mako'))
            options_map['**.mako'] = {'encoding': 'utf-8'}

        if not args.output_file:
            domain = args.domain if args.domain else settings.domain
            localedir = args.locale_directory \
                if args.locale_directory \
                else settings.localedirectory

            args.output_file = os.path.join(localedir, f'{domain}.pot')

        with open(args.output_file, 'wb') as outfile:
            catalog = Catalog(
                domain=args.domain,
                project=app.name,
                version=app.version,
                header_comment=CATALOG_HEADER,
                msgid_bugs_address=args.email,
                copyright_holder=args.copyright,
                language_team=args.language_team,
                charset='utf-8',
                fuzzy=False,
                creation_date=None,
            )

            for d in args.directories:
                self._extract(catalog, d, method_map, options_map,
                              args.ignore_directories)

            print(f'Writing PO template file to {args.output_file}')
            write_po(
                outfile,
                catalog,
                include_lineno=True,
                no_location=False,
                omit_header=False,
                sort_by_file=False,
                sort_output=False,
                width=79,
            )


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
        settings = app.settings.i18n
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
        settings = app.settings.i18n
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


class I18nCLI(SubCommand):
    __command__ = 'i18n'
    __arguments__ = [
        ExtractCommand,
        InitCommand,
        UpdateCommand,
        CompileCommand,
    ]
