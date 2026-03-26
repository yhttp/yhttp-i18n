import os

from bddcli import Given, Application as CLIApplication, status, stderr, stdout
from yhttp.core import Application

from yhttp.ext.i18n import install


_app = Application('0.1.0', 'foo')
install(_app)


def test_extract_minimal(mockupfs, tempdir, bddcli_bootpatch):
    tmpfs = mockupfs(**{
        'foo.py': 'foo = _(\'foo\')',
    })

    cliapp = CLIApplication('foo', f'{__name__}:_app.climain')
    args = [
        'i18n',
        'extract',
        f'--locale-directory {tempdir}',
        tmpfs
    ]
    outfile = f'{tempdir}/messages.pot'

    freezetime = \
        'import freezegun;' \
        'freezegun.freeze_time("2012-02-14 12:00:01+0000").start()\n'

    with bddcli_bootpatch(freezetime), Given(cliapp, args):
        assert stderr == ''
        assert status == 0
        assert stdout == \
            f'Extracting messages from: {tmpfs}\n' \
            f'Extracting messages from {tmpfs}/foo.py\n' \
            f'Writing PO template file to {outfile}\n'
        assert os.path.exists(f'{tempdir}/messages.pot')
        with open(outfile) as f:
            content = f.read()

        assert content == \
            '# Translations template for foo.\n' \
            '# Copyright (C) 2012 ORGANIZATION\n' \
            'msgid ""\n' \
            'msgstr ""\n' \
            '"Project-Id-Version: foo 0.1.0\\n"\n' \
            '"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"\n' \
            '"POT-Creation-Date: 2012-01-14 16:00+0400\\n"\n' \
            '"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n' \
            '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n' \
            '"Language-Team: LANGUAGE <LL@li.org>\\n"\n' \
            '"MIME-Version: 1.0\\n"\n' \
            '"Content-Type: text/plain; charset=utf-8\\n"\n' \
            '"Content-Transfer-Encoding: 8bit\\n"\n' \
            '"Generated-By: Babel 2.18.0\\n"\n' \
            '\n' \
            f'#: {tmpfs}/foo.py:1\n' \
            'msgid "foo"\n' \
            'msgstr ""\n\n'


def test_extract(mockupfs, tempdir, bddcli_bootpatch):
    tmpfs = mockupfs(**{
        'foo.py': 'foo = _(\'foo\')',
        'baz.txt': '_(\'baz\')',
        'foo.mako': '${_(\'bar\')}',
        'build': {
            'bar.py': 'bar = _(\'bar\'_)'
        }
    })

    cliapp = CLIApplication('foo', f'{__name__}:_app.climain')
    args = [
        'i18n',
        'extract',
        '--mako',
        '--ignore-file "**/*.txt"',
        '--ignore-directory build',
        '--copyright "foo bar"',
        '--language-team Alice',
        f'--locale-directory {tempdir}',
        '--email alice@example.com',
        tmpfs
    ]
    outfile = f'{tempdir}/messages.pot'

    # patch bddcli bootstrapper to emulate mako is not installed
    makopatch = \
        'import builtins;__import_backup__ = builtins.__import__\n' \
        'def __import_wrapper__(m, *a, **kw):\n' \
        '    if m == "mako":\n' \
        '        raise ModuleNotFoundError(f"No module named \'{m}\'")\n' \
        '    return __import_backup__(m, *a, **kw)\n' \
        'builtins.__import__ = __import_wrapper__\n'
    with bddcli_bootpatch(makopatch), Given(cliapp, args):
        assert stderr == 'Mako must be installed when using `--mako` flag\n'
        assert status == 255

    freezetime = \
        'import freezegun;' \
        'freezegun.freeze_time("2012-01-14 12:00:01").start()\n'
    with bddcli_bootpatch(freezetime), Given(cliapp, args):
        assert stderr == ''
        assert status == 0
        assert stdout == \
            f'Extracting messages from: {tmpfs}\n' \
            f'Extracting messages from {tmpfs}/foo.mako (encoding="utf-8")\n' \
            f'Extracting messages from {tmpfs}/foo.py\n' \
            f'Writing PO template file to {outfile}\n'
        assert os.path.exists(f'{tempdir}/messages.pot')
        with open(outfile) as f:
            content = f.read()

        assert content == \
            '# Translations template for foo.\n' \
            '# Copyright (C) 2012 foo bar\n' \
            'msgid ""\n' \
            'msgstr ""\n' \
            '"Project-Id-Version: foo 0.1.0\\n"\n' \
            '"Report-Msgid-Bugs-To: alice@example.com\\n"\n' \
            '"POT-Creation-Date: 2012-01-14 16:00+0400\\n"\n' \
            '"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n' \
            '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n' \
            '"Language-Team: Alice\\n"\n' \
            '"MIME-Version: 1.0\\n"\n' \
            '"Content-Type: text/plain; charset=utf-8\\n"\n' \
            '"Content-Transfer-Encoding: 8bit\\n"\n' \
            '"Generated-By: Babel 2.18.0\\n"\n' \
            '\n' \
            f'#: {tmpfs}/foo.mako:1\n' \
            'msgid "bar"\n' \
            'msgstr ""\n' \
            '\n' \
            f'#: {tmpfs}/foo.py:1\n' \
            'msgid "foo"\n' \
            'msgstr ""\n\n'
