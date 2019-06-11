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

`plugin.yml` defines which `actions`, `notification types` and `templates` plugin contains.

#### Actions

Actions are shortcuts to actual performed actions, therefore caller doesn't need to know implementation of these actions to execute them.

Actions section is a list of actions. Every action has `name`, `title` and `command` attributes.

```
actions:
  - name: dummy
    title: "{% trans %}Dummy action{% endtrans %}"
    command: /bin/true
```

* `name` is internal action name that would be used in api calls or from cli.
* `title` is description which should be shown to user to explain what that action does. It is possible to mark description as translatable with jinja `{% trans %}...{% endtrans %}` tags. 
* `command` is a string specifying what command will be actually executed.

#### Templates

Templates section is a list of templates. Every templates has `type`, `supported_media` and `src` attributes.

```
templates:
  - type: simple_message
    supported_media:
      - plain
      - html
    src: simple.j2
```

* `type` is name of template.
* `supported_media` is a list of media types that notification system is capable of rendering into.
* `src` is name of jinja template file.

#### Notifications types

Notification type is set of predefined options for notifications.

Notifications section is a list of notification types. Every notification type has mandatory `name`, `template`, `actions` and `version` attributes and few more optional. Optional attributes set additional default values 

```
notifications:
  - name: simple
    template: simple_message
    actions:
      - dummy
    version: 1
```

* `name` is name of notification type. Used when creating new notification.
* `template` is name of template from `templates` section.
* `actions` is a list of available actions from `actions` section.
* `versions` is integer that is used to check if notification type matches API version. Notification type is ignored if API version doesn't match.

Optional attributes:

* `severity`
* `persistent`
* `explicit_dismiss` is boolean value that decide if notification can be dismissed via `dismiss` action. When `explicit_dismiss` is `False`, notification can be dismissed only through calling other available actions.

#### Example plugin

```
actions:
  - name: reject
    title: "{% trans %}Reject current update{% endtrans %}"
    command: updater --reject-update
  - name: dummy
    title: "{% trans %}Dummy action{% endtrans %}"
    command: /bin/true
templates:
  - type: simple_message
    supported_media:
      - plain
      - html
    src: simple.j2
  - type: complex_message
    supported_media:
      - plain
      - html
      - email
    src: complex.j2
notifications:
  - name: simple
    template: simple_message
    actions:
      - dummy
    version: 1
  - name: complex
    template: complex_message
    severity: error
    persistent: True
    explicit_dismiss: False
    actions:
      - reject
    version: 1
```

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
