import functools

import bddrest
import pytest
from yhttp.core import Application

from yhttp.dev.fixtures import tempdir, mockupfs, bddcli_bootstrapper_patch


@pytest.fixture
def app():
    return Application('0.1.0', 'foo')


@pytest.fixture
def httpreq(app):
    return functools.partial(bddrest.Given, app)
