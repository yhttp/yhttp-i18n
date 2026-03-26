import os

from bddcli import Given, Application as CLIApplication, status, stderr, stdout
from yhttp.core import Application

from yhttp.ext.i18n import install


_app = Application('0.1.0', 'foo')
install(_app)


POT = \
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
    '#: /i18n/foo.mako:1\n' \
    'msgid "bar"\n' \
    'msgstr ""\n' \
    '\n' \
    '#: /i18n/foo.py:1\n' \
    'msgid "foo"\n' \
    'msgstr ""\n\n'


def test_init_minimal(mockupfs, bddcli_bootpatch):
    tmpfs = mockupfs(**{
        'messages.pot': POT,
    })

    cliapp = CLIApplication('foo', f'{__name__}:_app.climain')
    args = [
        'i18n',
        'init',
        f'--locale-directory {tmpfs}',
        'fa',
    ]

    freezetime = \
        'import freezegun;' \
        'freezegun.freeze_time("2012-02-14 12:00:01+0000").start()\n'

    outfile = f'{tmpfs}/fa/LC_MESSAGES/messages.po'
    with bddcli_bootpatch(freezetime), Given(cliapp, args):
        assert stderr == ''
        assert status == 0
        assert stdout == \
            f'Creating catalog {tmpfs}/fa/LC_MESSAGES/messages.po ' \
            f'based on {tmpfs}/messages.pot\n'

        assert os.path.exists(outfile)
        with open(outfile) as f:
            content = f.read()

        assert content == \
            '# Persian translations for foo.\n' \
            '# Copyright (C) 2012 foo bar\n' \
            'msgid ""\n' \
            'msgstr ""\n' \
            '"Project-Id-Version: foo 0.1.0\\n"\n' \
            '"Report-Msgid-Bugs-To: alice@example.com\\n"\n' \
            '"POT-Creation-Date: 2012-01-14 16:00+0400\\n"\n' \
            '"PO-Revision-Date: 2012-01-14 16:00+0400\\n"\n' \
            '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n' \
            '"Language: fa\\n"\n' \
            '"Language-Team: Alice\\n"\n' \
            '"Plural-Forms: nplurals=1; plural=0;\\n"\n' \
            '"MIME-Version: 1.0\\n"\n' \
            '"Content-Type: text/plain; charset=utf-8\\n"\n' \
            '"Content-Transfer-Encoding: 8bit\\n"\n' \
            '"Generated-By: Babel 2.18.0\\n"\n' \
            '\n' \
            '#: /i18n/foo.mako:1\n' \
            'msgid "bar"\n' \
            'msgstr ""\n' \
            '\n' \
            '#: /i18n/foo.py:1\n' \
            'msgid "foo"\n' \
            'msgstr ""\n\n'
