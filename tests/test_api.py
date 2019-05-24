import pytest

from notifylib import Api
from notifylib.exceptions import (
    InvalidOptionsError,
    MediaTypeNotAvailableError,
    NoSuchActionError,
    NoSuchNotificationError,
    NoSuchNotificationSkeletonError,
)


def test_config_file(api_conf_from_file):
    assert isinstance(api_conf_from_file, Api)


def test_config_dict(api):
    assert isinstance(api, Api)


def test_list_templates(api):
    templates = api.get_templates()

    assert templates == ['simple.empty', 'simple.simple', 'simple.complex']


def test_list_notifications(api, user_opts):
    nid = api.create(**user_opts)
    nid2 = api.create(**user_opts)

    notifications = api.get_notifications()

    assert len(notifications.items()) == 2
    assert nid in notifications
    assert nid2 in notifications


def test_create_notification(api, user_opts):
    api.create(**user_opts)
    notifications = api.get_notifications()

    assert len(notifications.items()) == 1


def test_create_volatile_notification(api, user_opts):
    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid)

    assert n['metadata']['persistent'] is False


def test_create_persistent_notification(api, user_opts):
    user_opts['persistent'] = True

    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid)

    assert n['metadata']['persistent'] is True


def test_create_nondismissable_notification(api, user_opts):
    user_opts['explicit_dismiss'] = False

    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid)

    assert 'dismiss' not in n['actions']


@pytest.mark.parametrize('skeleton_id', ['foo.bar', 'simple.foo', 'foo.simple'])
def test_create_notification_with_nonexisting_template(api, user_opts, skeleton_id):
    user_opts['skel_id'] = skeleton_id

    with pytest.raises(NoSuchNotificationSkeletonError):
        api.create(**user_opts)


@pytest.mark.parametrize('severity', ['info', 'warning', 'error', 'announcement', 'action_needed'])
def test_create_notification_with_severity(api, user_opts, severity):
    user_opts['severity'] = severity

    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid)

    assert n['metadata']['severity'] == severity


def test_create_notification_with_invalid_severity(api, user_opts):
    user_opts['severity'] = 'foobar'

    with pytest.raises(InvalidOptionsError):
        api.create(**user_opts)


def test_create_notification_with_default_default_action(api, user_opts):
    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid)

    assert n['metadata']['default_action'] == 'dismiss'


def test_create_notification_with_custom_default_action(api, user_opts):
    user_opts['default_action'] = 'dummy'

    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid)

    assert n['metadata']['default_action'] == 'dummy'


def test_create_notification_with_invalid_default_action(api, user_opts):
    user_opts['default_action'] = 'foobar'

    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid)

    assert n['metadata']['default_action'] == 'dismiss'


@pytest.mark.xfail
def test_create_notification_with_custom_action_timeout():
    pass


def test_get_notification(api, user_opts):
    nid = api.create(**user_opts)
    notifications = api.get_notifications()

    assert len(notifications.items()) == 1

    n = api.get_rendered_notification(nid)

    # very basic structure check
    # notification should have three key-value pairs
    assert len(n.keys()) == 3


def test_get_nonexisting_notification(api):
    with pytest.raises(NoSuchNotificationError):
        api.get_rendered_notification('12345678')


def test_get_notification_shortid(api, user_opts):
    nid = api.create(**user_opts)
    short_nid = nid[:8]
    n = api.get_rendered_notification(short_nid)

    assert len(n.keys()) == 3


def test_get_multiple_notifications(api, user_opts):
    """Test rendering multiple notifications in one session"""
    nid = api.create(**user_opts)
    nid2 = api.create(**user_opts)

    notifications = api.get_notifications()

    assert len(notifications.items()) == 2

    n = api.get_rendered_notification(nid)
    n2 = api.get_rendered_notification(nid2)

    assert len(n.keys()) == 3
    assert len(n2.keys()) == 3


def test_get_notification_nonexisting_media_type(api, user_opts):
    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid, 'foobar')

    assert len(n.keys()) == 3


def test_get_notification_force_media_type(api, user_opts):
    nid = api.create(**user_opts)
    n = api.get_rendered_notification(nid, 'html', force_media_type=True)

    assert len(n.keys()) == 3


def test_get_notification_force_media_type_failure(api, user_opts):
    nid = api.create(**user_opts)

    with pytest.raises(MediaTypeNotAvailableError):
        api.get_rendered_notification(nid, 'foobar', force_media_type=True)


def test_dismiss_notification(api, user_opts):
    nid = api.create(**user_opts)
    api.call_action(nid, 'dismiss')

    notifications = api.get_notifications()

    assert len(notifications.items()) == 0


def test_dismiss_nondismisable_notification(api, user_opts):
    user_opts['explicit_dismiss'] = False
    nid = api.create(**user_opts)

    with pytest.raises(NoSuchActionError):
        api.call_action(nid, 'dismiss')


def test_call_action(api, user_opts):
    nid = api.create(**user_opts)
    api.call_action(nid, 'dummy')

    notifications = api.get_notifications()

    assert len(notifications.items()) == 0


def test_call_action_shortid(api, user_opts):
    nid = api.create(**user_opts)
    short_nid = nid[:8]
    api.call_action(short_nid, 'dummy')

    notifications = api.get_notifications()

    assert len(notifications.items()) == 0


def test_call_default_action(api, user_opts):
    nid = api.create(**user_opts)
    api.call_action(nid, 'default')

    notifications = api.get_notifications()

    assert len(notifications.items()) == 0


def test_call_nonexisting_action(api, user_opts):
    nid = api.create(**user_opts)

    with pytest.raises(NoSuchActionError):
        api.call_action(nid, 'fooaction')


def test_call_action_on_nonexisting_notification(api, user_opts):
    with pytest.raises(NoSuchNotificationError):
        api.call_action('12345678', 'default')
