# Notification system

Notification system is tool that offers easy way to create and read notifications. Intended mainly for router infrastructure, but also usable for user supplied programs. It is extensible via plugins.

It is usable either as python library or directly from command line.

## How it works

Notification system uses predefined `notification types` for specific events (e.g. Approval of update, restart required, etc.) with predefined available actions.

E.g.: In case of "Approve update" user has two options: Approve or reject update.

Actions serve as shortcuts to actual performed actions, therefore caller of these actions doesn't need to know implementation of these actions to perform them.

`notification types` and `actions` are defined in plugins.

### Plugins

TBD

## i18n

Notification system enable internationalization of templates via babel.

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

## Legacy compatibility

Notification system offers basic backward compatibility with `user-notify` and should be sufficient drop-in replacement in most cases via included `create_notification` and `list_notifications` scripts. 
