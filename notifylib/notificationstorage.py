import os

from .logger import logger
from .notification import Notification


class NotificationStorage:
    """In-memory notification storage that serialize and deserialize them"""
    def __init__(self, volatile_dir, persistent_dir):
        # print("Constructing new NotifyStorage")
        self.storage_dirs = {
            'persistent': persistent_dir,
            'volatile': volatile_dir,
        }

        self.notifications = {}
        self.rendered = {}

        self.load(volatile_dir)
        self.load(persistent_dir)

    def store(self, n):
        """
        Store in memory
        serializate to disk
        render fallback in default languages
        """
        self.notifications[n.notif_id] = n

        if n.persistent:
            storage_dir = self.storage_dirs['persistent']
        else:
            storage_dir = self.storage_dirs['volatile']

        json_data = n.serialize()

        # save to disk
        file_path = os.path.join(storage_dir, "{}.json".format(n.notif_id))
        # TODO: try/catch
        with open(file_path, 'w') as f:
            f.write(json_data)

    def load(self, storage_dir):
        """Deserialize from FS"""
        logger.debug("Deserializing notifications from '%s'" % storage_dir)
        for root, dir, files in os.walk(storage_dir):
            for f in files:
                filepath = os.path.join(storage_dir, f)
                logger.debug("File %s" % filepath)

                n = Notification.from_file(filepath)
                self.notifications[n.notif_id] = n

    # TODO: find better key to identify notification instance in dict
    # name -> msgid
    def get_notification(self, name, media_type, lang):
        """Return notification either cached or if missing, cache it and return"""
        if (name, media_type, lang) not in self.rendered:
            self.rendered[(name, media_type, lang)] = self.notifications[name].render(media_type, lang)

        return self.rendered[(name, media_type, lang)]

    def get_all(self):
        return self.notifications

    # # TODO: WIP helper fce
    # def render_one(self, notif):
    #     pass

    # def render_all(self):
    #     """Render all notifications"""
    #     for n in self.notifications:
    #         self.render_one(n)
