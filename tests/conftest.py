import json
import pytest

from pathlib import Path
from notifylib import Api


@pytest.fixture
def volatile_dir(tmpdir):
    return tmpdir.mkdir('volatile')


@pytest.fixture
def persistent_dir(tmpdir):
    return tmpdir.mkdir('persistent')


@pytest.fixture
def config_dict(volatile_dir, persistent_dir):
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
def api(config_dict):
    return Api(confdict=config_dict)


@pytest.fixture
def api_conf_from_file():
    config_file = Path(__file__).parent.joinpath('files/config.conf')
    return Api(conffile=config_file)
