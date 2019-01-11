# TODO: use common name for all - Exceptions? Errors?

class NotifylibError(Exception):
    pass

class NotificationTemplatingError(NotifylibError):
    pass

class CreateNotificationError(NotifylibError):
    pass

class NoSuchActionException(NotifylibError):
    pass

class MediaTypeNotAvailableException(NotifylibError):
    pass

class NoSuchNotificationException(NotifylibError):
    pass

class NoSuchNotificationSkeletonException(NotifylibError):
    pass

class NotificationNotDismissibleException(NotifylibError):
    pass

class NotificationStorageException(NotifylibError):
    pass
