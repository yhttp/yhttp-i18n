import os

from bddcli import Given, Application as CLIApplication, status, stderr, stdout
from yhttp.core import Application

from yhttp.ext.i18n import install


_app = Application('0.1.0', 'foo')
install(_app)


PO = \
    '# Persian translations for foo.\n' \
    '# Copyright (C) 2012 foo bar\n' \
    'msgid ""\n' \
    'msgstr ""\n' \
    '"Project-Id-Version: foo 0.1.0\\n"\n' \
    '"Report-Msgid-Bugs-To: alice@example.com\\n"\n' \
    '"POT-Creation-Date: 2012-01-14 12:00+0000\\n"\n' \
    '"PO-Revision-Date: 2012-01-14 12:00+0000\\n"\n' \
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
    'msgstr "بار"\n' \
    '#: /i18n/foo.py:1\n' \
    'msgid "foo"\n' \
    'msgstr "فو"\n\n' \
    '#: /i18n/foo.py:2\n' \
    'msgid "baz"\n' \
    'msgstr ""\n' \
    '#: /i18n/foo.py:3\n' \
    'msgid "qux %s"\n' \
    'msgstr "qux"\n'


def test_init_minimal(mktmptree, bddcli_bootpatch):
    tmpfs = mktmptree({
        'fa': {
            'LC_MESSAGES': {
                'messages.po': PO
            },
        },
        'foo': 'lorem ipsum',
    })

    cliapp = CLIApplication('foo', f'{__name__}:_app.climain')
    args = [
        'i18n',
        'compile',
        f'--locale-directory {tmpfs}',
    ]

    freezetime = \
        'import freezegun;' \
        'freezegun.freeze_time("2012-02-14 12:00:01+0000").start()\n'

    infile = f'{tmpfs}/fa/LC_MESSAGES/messages.po'
    outfile = f'{tmpfs}/fa/LC_MESSAGES/messages.mo'
    with bddcli_bootpatch(freezetime), Given(cliapp, args):
        assert stderr == ''
        assert status == 0
        print(stdout)
        assert stdout == \
            f'3 of 4 messages (75%) translated in {infile}\n' \
            f'error: {infile}:29: placeholders are incompatible\n' \
            f'Compiling catalog {outfile} based on {infile}\n' \
            '1 error(s) encountered.\n'

        assert os.path.exists(outfile)
    #     with open(outfile) as f:
    #         content = f.read()

    # when target catalog does not exists
    os.mkdir(os.path.join(tmpfs, 'ar'))
    with Given(cliapp, args):
        assert stderr == f'Catalog {tmpfs}/ar/LC_MESSAGES/messages.po not ' \
            'exists, init first\n'
        assert status == 1
