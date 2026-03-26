VENV_NAME = yhttp
PKG_NAMESPACE = yhttp.ext.i18n
PKG_NAME = yhttp-i18n
TIMEZONE = UTC
PYTEST_FLAGS = -vv
PYDEPS_COMMON = \
	'coveralls' \
	'freezegun' \
	'pytest-mock' \
	'bddrest >= 6.1, < 7' \
	'bddcli >= 2.10.1, < 3' \
	'yhttp-dev >= 3.4.2' \
	'mako'


# Assert the python-makelib version
PYTHON_MAKELIB_VERSION_REQUIRED = 2.2


# Ensure the python-makelib is installed
PYTHON_MAKELIB_PATH = /usr/local/lib/python-makelib
ifeq ("", "$(wildcard $(PYTHON_MAKELIB_PATH))")
  MAKELIB_URL = https://github.com/pylover/python-makelib
  $(error python-makelib is not installed. see "$(MAKELIB_URL)")
endif


# Include a proper bundle rule file.
include $(PYTHON_MAKELIB_PATH)/venv-lint-test-pypi.mk
