class NotifylibError(Exception):
    pass

class NotificationTemplatingError(NotifylibError):
    pass

class CreateNotificationError(NotifylibError):
    pass

class NoSuchActionException(Exception):
    pass

class NoSuchNotificationException(Exception):
    pass

class NotificationNotDismissibleException(Exception):
    pass
