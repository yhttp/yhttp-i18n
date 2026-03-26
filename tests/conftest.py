import functools

import bddrest
import pytest
from yhttp.core import Application
from bddcli.fixtures import bootstrapper_patch
from yhttp.dev.fixtures import tempdir, mockupfs


@pytest.fixture
def bddcli_bootpatch():
    return bootstrapper_patch


@pytest.fixture
def app():
    return Application('0.1.0', 'foo')


@pytest.fixture
def httpreq(app):
    return functools.partial(bddrest.Given, app)
