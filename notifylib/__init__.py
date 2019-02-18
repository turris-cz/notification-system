import os.path

__all__ = [
    'api',
    'exceptions',
    'notification',
    'notificationskeleton',
    'notificationstorage',
    'plugin',
    'pluginstorage',
    'sorting',
    'supervisor',
]

__version__ = '0.1'
__module_path__ = os.path.dirname(os.path.abspath(__file__))

# put it elsewhere?
api_version = 1
