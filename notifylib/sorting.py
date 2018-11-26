from .logger import logger


class Sorting:
    """Builtin sorting for notifications"""
    SEVERITY = {
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'ANNOUNCEMENT': 10,
        'ACTION_NEEDED': 25,
    }

    @staticmethod
    def by_timestamp(param):
        return param[1]['metadata']['timestamp']

    @staticmethod
    def by_severity(param):
        severity = param[1]['metadata']['severity'].upper()
        return Sorting.SEVERITY[severity]

    @staticmethod
    def sort_by(notifications, criterion, reverse=None):
        if criterion in Sorting.SORT_ARGS:
            key_func, default_reverse = Sorting.SORT_ARGS[criterion]

            if reverse is None:
                reverse = default_reverse

            logger.debug("Using function '%s' to sort", key_func.__name__)
            new = sorted(notifications.items(), key=key_func, reverse=reverse)

            return dict(new)

        return notifications

    # criterion: {key_function, reverse}
    SORT_ARGS = {
        'severity': [by_severity.__func__, True],
        'timestamp': [by_timestamp.__func__, True]
    }
