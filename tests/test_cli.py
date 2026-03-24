from bddcli import Given, Application as CLIApplication, status, stderr
from yhttp.core import Application

from yhttp.ext.i18n import install


_app = Application('0.1.0', 'foo')
install(_app)


def test_cli():
    cliapp = CLIApplication('foo', 'tests.test_cli:_app.climain')
    with Given(cliapp, 'i18n --help'):
        assert status == 0
        assert stderr == ''
