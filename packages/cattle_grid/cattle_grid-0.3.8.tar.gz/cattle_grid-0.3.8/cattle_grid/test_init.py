from .testing.fixtures import auth_config_file  # noqa

from . import create_app


def test_create_app(auth_config_file):  # noqa
    create_app([auth_config_file])
