class Severity:
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    ANNOUNCEMENT = 'announcement'
    ACTION_NEEDED = 'action_needed'

    # severities for legacy compatibility
    LEGACY_RESTART = 'restart'
    LEGACY_ERROR = 'error'
    LEGACY_UPDATE = 'update'
    LEGACY_NEWS = 'news'

    STANDARD = [INFO, WARNING, ERROR, ANNOUNCEMENT, ACTION_NEEDED]

    # translations of severity levels between new and old behaviour
    STD_TO_LEGACY = {
        ACTION_NEEDED: LEGACY_RESTART,
        ERROR: LEGACY_ERROR,
        INFO: LEGACY_UPDATE,
        ANNOUNCEMENT: LEGACY_NEWS,
        WARNING: LEGACY_ERROR,
    }

    LEGACY_TO_STD = {
        LEGACY_RESTART: ACTION_NEEDED,
        LEGACY_ERROR: ERROR,
        LEGACY_UPDATE: INFO,
        LEGACY_NEWS: ANNOUNCEMENT,
    }

    @classmethod
    def legacy_to_standard(cls, severity):
        return cls.LEGACY_TO_STD[severity]

    @classmethod
    def standard_to_legacy(cls, severity):
        return cls.STD_TO_LEGACY[severity]
