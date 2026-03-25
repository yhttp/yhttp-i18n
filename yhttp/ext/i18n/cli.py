import os
import sys
import fnmatch

from babel.messages.extract import extract_from_dir
from babel.messages.pofile import write_po
from babel.messages.catalog import Catalog

from easycli import SubCommand, Argument


CATALOG_HEADER = \
    '# Translations template for PROJECT.\n' \
    '# Copyright (C) YEAR ORGANIZATION\n'


# '# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\n#'


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
                'N_': None,
                '_': None,
                'dgettext': (2,),
                'dngettext': (2, 3),
                'dnpgettext': ((2, 'c'), 3, 4),
                'dpgettext': ((2, 'c'), 3),
                'gettext': None,
                'ngettext': (1, 2),
                'npgettext': ((1, 'c'), 2, 3),
                'pgettext': ((1, 'c'), 2),
                'ugettext': None,
                'ungettext': (1, 2)
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
        settings = app.i18n.settings

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


class I18nCLI(SubCommand):
    __command__ = 'i18n'
    __arguments__ = [
        ExtractCommand,
    ]
