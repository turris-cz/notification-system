class NotifylibError(Exception):
    pass


class NotificationTemplatingError(NotifylibError):
    pass


class CreateNotificationError(NotifylibError):
    pass


class NoSuchActionError(NotifylibError):
    pass


class MediaTypeNotAvailableError(NotifylibError):
    pass


class NoSuchTemplateError(NotifylibError):
    pass


class NoSuchNotificationError(NotifylibError):
    pass


class NoSuchNotificationSkeletonError(NotifylibError):
    pass


class NotificationNotDismissibleError(NotifylibError):
    pass


class NotificationStorageError(NotifylibError):
    pass


class VersionMismatchError(NotifylibError):
    pass


class InvalidOptionsError(NotifylibError):
    pass
