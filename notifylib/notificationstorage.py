import logging
import os
from datetime import datetime as dt

from .notification import Notification


class NotificationStorage:
    """In-memory notification storage that serialize and deserialize them"""
    def __init__(self, volatile_dir, persistent_dir, notification_types):
        print("Constructing new NotifyStorage")
        self.init_logger()
        self.load(volatile_dir)
        self.load(persistent_dir)

        self.storage_dirs = {
            'persistent': persistent_dir,
            'volatile': volatile_dir,
            'fallback': None,  # TBD
        }

        self.notification_types = notification_types  # notification data types/templates
        self.notifications = []
        # self.cached = {}

    def init_logger(self):
        self.logger = logging.getLogger("notifylib")

    def store(self, n):
        """Store in memory and serializate to disk"""
        self.notifications.append(n)
        self.serialize(n)

    def serialize(self, n):
        """..."""
        if n.persistent:
            storage_dir = self.storage_dirs['persistent']
        else:
            storage_dir = self.storage_dirs['volatile']

        # fallback_render_dir = storage_dirs['render_fallback']
        # do something to render content
        # fallback_content = n.render()
        metadata_content = n.serialize_metadata()

        fileid = self.generate_id()

        # save to disk
        regular_file = os.path.join(storage_dir, "{}.json".format(fileid))
        # fallback_file =  os.path.join(fallback_render_dir, fileid)
        # TODO: try/catch
        with open(regular_file, 'w') as f:
            f.write(metadata_content)

        # with open(fallback_file, 'w') as f:
        #     f.write(fallback_content)

    def load(self, storage_dir):
        """Deserialize from FS"""

        # for f in ls storage_dir:
        #   n = NotificationType.from_file(f)
        #   if not n.valid():
        #       delete_from_fs()

    # TODO: find better key to identify notification instance in dict
    def get_new_instance(self, **opts):
        """Return complete new notification instance based on notification type"""
        self.logger.debug("Trying to create from template %s" % opts['template'])

        timestamp = dt.utcnow()

        return Notification(timestamp, self.notification_types[opts['template']], **opts)

    # TODO: find better key to identify notification instance in dict
    def get_notification(self, name):
        """Return notification either cached or if missing, cache it and return"""
        if not self.cached[name]:
            # do something to create/cache
            # do it inside serialization
            pass
        return self.cached[name]

    def get_all(self):
        return self.notifications

    def get_notification_types(self):
        """Return all notification types"""
        return self.notification_types

    # # TODO: WIP helper fce
    # def render_one(self, notif):
    #     pass

    # def render_all(self):
    #     """Render all notifications"""
    #     for n in self.notifications:
    #         self.render_one(n)

    def generate_id(self):
        """Unique id of message based on timestamp"""
        return dt.utcnow().timestamp()
