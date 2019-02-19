import json
import pytest

from notifylib.api import Api


@pytest.fixture
def volatile_dir(tmpdir):
    return tmpdir.mkdir('volatile')


@pytest.fixture
def persistent_dir(tmpdir):
    return tmpdir.mkdir('persistent')


@pytest.fixture
def config(volatile_dir, persistent_dir):
    return {
        'settings': {
            'volatile_dir': volatile_dir,
            'persistent_dir': persistent_dir,
        }
    }


@pytest.fixture
def user_opts():
    return {
        'skel_id': 'simple.simple',
        'data': json.loads('{"message": "dragons kittens turtles sloths"}')
    }


@pytest.fixture
def api(config):
    return Api(confdict=config)
