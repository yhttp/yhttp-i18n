import os

from bddcli import Given, Application as CLIApplication, status, stderr, stdout
from yhttp.core import Application

from yhttp.ext.i18n import install


_app = Application('0.1.0', 'foo')
install(_app)


def test_cli_help():
    cliapp = CLIApplication('foo', 'tests.test_cli:_app.climain')
    with Given(cliapp, 'i18n --help'):
        print(stderr)
        assert status == 0
        assert stderr == ''

    # with Given(cliapp, 'i18n extract --help'):
    #     assert stderr == ''
    #     print(stdout)
    #     assert status == 1


def test_extract(mockupfs, tempdir, bddcli_bootstrapper_patch):
    tmpfs = mockupfs(**{
        'foo.py': 'foo = _(\'foo\')',
        'foo.mako': '${_(\'bar\')}'
    })

    cliapp = CLIApplication('foo', 'tests.test_cli:_app.climain')
    args = [
        'i18n',
        'extract',
        '--mako',
        '--copyright "foo bar"',
        '--language-team Alice',
        f'--locale-directory {tempdir}',
        '--email alice@example.com',
        tmpfs
    ]
    outfile = f'{tempdir}/messages.pot'

    freezetime = \
        'import freezegun;' \
        'freezegun.freeze_time("2012-01-14 12:00:01").start()\n'
    with bddcli_bootstrapper_patch(freezetime), Given(cliapp, args):
        print(stderr)
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

        print(content)
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
