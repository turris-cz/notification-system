import logging
import os
from datetime import datetime as dt

from .notification import Notification


class NotificationStorage:
    """In-memory notification storage that serialize and deserialize them"""
    def __init__(self, volatile_dir, persistent_dir):
        # print("Constructing new NotifyStorage")
        self.init_logger()

        self.storage_dirs = {
            'persistent': persistent_dir,
            'volatile': volatile_dir,
            'fallback': None,  # in notification itself
        }

        self.notifications = {}
        # self.cached = {}

        self.load(volatile_dir)
        self.load(persistent_dir)

    def init_logger(self):
        self.logger = logging.getLogger("notifylib")

    def store(self, n):
        """Store in memory and serializate to disk"""
        self.notifications[n.notif_id] = n

        if n.persistent:
            storage_dir = self.storage_dirs['persistent']
        else:
            storage_dir = self.storage_dirs['volatile']

        # fallback_render_dir = storage_dirs['render_fallback']
        # do something to render content
        # fallback_content = n.render()

        # metadata_content = n.serialize_metadata()
        content = n.serialize()

        # fileid = self.generate_id()
        fileid = n.notif_id

        # save to disk
        regular_file = os.path.join(storage_dir, "{}.json".format(fileid))
        # fallback_file =  os.path.join(fallback_render_dir, fileid)
        # TODO: try/catch
        with open(regular_file, 'w') as f:
            f.write(content)

        # with open(fallback_file, 'w') as f:
        #     f.write(fallback_content)

    def load(self, storage_dir):
        """Deserialize from FS"""
        self.logger.debug("Deserializing notifications from '%s'" % storage_dir)
        for root, dir, files in os.walk(storage_dir):
            for f in files:
                filepath = os.path.join(storage_dir, f)
                self.logger.debug("File %s" % filepath)

                n = Notification.from_file(filepath)
                self.notifications[n.notif_id] = n

    # TODO: find better key to identify notification instance in dict
    # name -> msgid
    def get_notification(self, name):
        """Return notification either cached or if missing, cache it and return"""
        if not self.cached[name]:
            # do something to create/cache
            # do it inside serialization
            pass
        return self.cached[name]

    def get_all(self):
        return self.notifications

    # # TODO: WIP helper fce
    # def render_one(self, notif):
    #     pass

    # def render_all(self):
    #     """Render all notifications"""
    #     for n in self.notifications:
    #         self.render_one(n)
