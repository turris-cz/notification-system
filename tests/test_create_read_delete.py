import json
import pytest

from notifylib.api import Api


@pytest.fixture
def volatile_dir(tmpdir):
    return tmpdir.mkdir('notify').mkdir('volatile')


@pytest.fixture
def config(volatile_dir):
    return {
        'settings': {
            'volatile_dir': volatile_dir,
        }
    }


@pytest.mark.xfail
def test_create_notification(tmpdir, volatile_dir, config):
    content = '''{
    "notif_id": "8c3ad32ca1774eed985604cc1a328773",
    "api_version": 1,
    "timestamp": 1549381864,
    "skeleton": {
        "name": "simple",
        "plugin_name": "simple",
        "version": 1,
        "template": {
            "type": "simple_message",
            "supported_media": [
                "plain",
                "html"
            ],
            "src": "simple.j2"
        },
        "actions": {
            "dummy": {
                "name": "dummy",
                "title": "{% trans %}Dummy action{% endtrans %}",
                "command": "/bin/true"
            }
        },
        "timeout": null,
        "severity": "info",
        "persistent": false,
        "explicit_dismiss": true
    },
    "persistent": false,
    "timeout": null,
    "severity": "info",
    "data": {
        "message": "egg egg spam"
    },
    "fallback": {
        "plain": "\\n= Simple message =\\nMessage: egg egg spam\\n",
        "html": "\\n<h3>Simple message</h3>\\n<p>\\n    HTML rendered message: egg egg spam\\n</p>\\n"
    },
    "valid": true,
    "explicit_dismiss": true,
    "default_action": "dismiss"
}'''

    # TODO: figure out what to do with timestamp and notification id

    api = Api(confdict=config)
    opts = {
        'skel_id': 'simple.simple',
        'data': json.loads('{"message": "egg spam spam"}'),
    }

    nid = api.create(**opts)

    assert nid.isalnum() and len(nid) == 32

    f = volatile_dir.join("{}.json".format(nid))
    result = f.read()

    assert result == content


def test_get_notification(tmpdir, volatile_dir, config):
    content = '''{
    "notif_id": "8c3ad32ca1774eed985604cc1a328773",
    "api_version": 1,
    "timestamp": 1549381864,
    "skeleton": {
        "name": "simple",
        "plugin_name": "simple",
        "version": 1,
        "template": {
            "type": "simple_message",
            "supported_media": [
                "plain",
                "html"
            ],
            "src": "simple.j2"
        },
        "actions": {
            "dummy": {
                "name": "dummy",
                "title": "{% trans %}Dummy action{% endtrans %}",
                "command": "/bin/true"
            }
        },
        "timeout": null,
        "severity": "info",
        "persistent": false,
        "explicit_dismiss": true
    },
    "persistent": false,
    "timeout": null,
    "severity": "info",
    "data": {
        "message": "egg egg spam"
    },
    "fallback": {
        "plain": "\\n= Simple message =\\nMessage: egg egg spam\\n",
        "html": "\\n<h3>Simple message</h3>\\n<p>\\n    HTML rendered message: egg egg spam\\n</p>\\n"
    },
    "valid": true,
    "explicit_dismiss": true,
    "default_action": "dismiss"
}'''

    f = volatile_dir.join('8c3ad32ca1774eed985604cc1a328773.json')
    f.write(content)

    api = Api(confdict=config)
    n = api.get_rendered_notification('8c3ad32ca1774eed985604cc1a328773', 'plain', 'en')

    assert isinstance(n, dict)

    # TODO: check json schema?

    assert 'message' in n
    assert 'actions' in n
    assert 'metadata' in n

    assert n['message'] == '\n= Simple message =\nMessage: egg egg spam\n'
    assert set(('dummy', 'dismiss')).issubset(n['actions'])
    assert set(('persistent', 'timestamp', 'severity', 'default_action')).issubset(n['metadata'])
