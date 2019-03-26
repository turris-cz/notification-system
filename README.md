# Notification system

Notification system is tool that offers easy way to create and read notifications. It is intended mainly for router infrastructure, but it is also usable from user supplied programs.

Notification system is extensible via plugins and allows internationalization via babel.

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

### Sample program

TBD

## How it works

Notification system uses predefined `notification types` for specific events (e.g. Approval of update, restart required, etc.) with predefined responses to these events.

E.g.: In case of "Approve update" user has two options: Approve or reject update.


### Plugins

Plugins consist of general plugin definition `plugin.yml` and template files. Templates are written as jinja templates and defines how will specific messages look.

`plugin.yml` defines what `actions`, `notification types` and `templates` plugin contains.

Sample plugin looks like this:

```
plugins
├── simple
    ├── plugin.yml
    └── templates
        ├── complex.j2
        └── simple.j2
```

[...]

Actions are shortcuts to actual performed actions, therefore caller doesn't need to know implementation of these actions to execute them.

### i18n

TBD

## Legacy compatibility

Notification system offers basic backward compatibility with `user-notify` and should be sufficient drop-in replacement in most cases via included `create_notification` and `list_notifications` scripts. 
