class NotifylibError(Exception):
    pass

class NotificationTemplatingError(NotifylibError):
    pass

class CreateNotificationError(NotifylibError):
    pass

class NoSuchNotificationException(Exception):
    pass
