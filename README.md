# Notification system

Notification system is tool that offers easy way to create and read notifications. It is intended mainly for router infrastructure, but it is also usable from user supplied programs.

Notification system is extensible with plugins and allows internationalization via babel.

You can use it either directly from your code as python library or interactively from command line.

## Usage

### CLI interface


Use `notify-cli` with one of following commands:

```
add                 Add new notification
list                List various things
get                 Get specific message
call                Call actions on messages
```

For full options see help:

```
notify-cli --help
```

### Library API

```
from notifylib import Api

api = Api()
# do something with Api
```

## Sample program

Following code will create, retrieve and then dismiss notification.

```
import json
import pprint

from notifylib.api import Api

template = 'simple.simple'
message_data = '{"message": "Hello world!"}'
opts = {
    'skel_id': template,
    'data': json.loads(message_data),
}

api = Api()

# Create notification
nid = api.create(**opts)

# Retreive
n = api.get_rendered_notification(nid)
pprint.pprint(n)

# Delete
api.call_action(nid, 'dismiss')
```

## How it works

Notification system uses predefined `notification types` for specific events (e.g. Approval of update, restart required) with predefined responses.

For instance: "Approve update" has two options: Approve or reject update.


### Plugins

Plugin consist of general plugin definition (`plugin.yml`) and template files (`templates/*.j2`). Templates are written as jinja templates and there is exactly one template per event.

`plugin.yml` defines which `actions`, `notification types` and `templates` plugin contains.

Sample plugin structure looks like this:

```
plugins/
├── simple
│   ├── plugin.yml
│   └── templates
│       └── empty.j2
└── storage
    ├── plugin.yml
    └── templates
        ├── srv_symlinked.j2
        └── succesfully_moved.j2
```

[...]

#### Actions

Actions are shortcuts to actual performed actions, therefore caller doesn't need to know implementation of these actions to execute them.

### i18n

TBD

## Legacy compatibility

Notification system offers basic backward compatibility with `user-notify` and should be sufficient drop-in replacement in most cases via included `create_notification`, `list_notifications` and  `user-notify-display` scripts. 

## Technical notes

Synchronization is lock-free using behind the scene built-in Linux synchronization primitives. Note that this behavior is highly platform dependent and might not work as intended on other platforms.

Multiple instances of Notification system can run alongside each other (e.g. multiple writers with multiple readers) and be up-to-date via combination of RCU-like synchronization and BASE consistency.
Notification system does only three operations on notifications:

* create
* read
* delete

Therefore there is no need of explicit locking as `unlink()` is atomic operation on Linux.
