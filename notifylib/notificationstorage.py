import os
import subprocess

from datetime import datetime as dt

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

    def get_notification(self, msgid, media_type, lang):
        """Return notification either cached or if missing, cache it and return"""
        if (msgid, media_type, lang) not in self.rendered:
            self.rendered[(msgid, media_type, lang)] = self.notifications[msgid].render(media_type, lang)

        return self.rendered[(msgid, media_type, lang)]

    def get_all(self):
        return self.notifications

    # # TODO: WIP helper fce
    # def render_one(self, notif):
    #     pass

    # def render_all(self):
    #     """Render all notifications"""
    #     for n in self.notifications:
    #         self.render_one(n)

    def delete_messages(self):
        """Delete messages based on their timeout"""
        to_delete = []
        now = dt.utcnow()

        for n in self.notifications.values():
            if not n.valid(now):
                to_delete.append(n)

        for n in to_delete:
            self.dismiss(n.notif_id)
            logger.debug("Deleting notification '{}' due to timeout".format(n.notif_id))

    def dismiss(self, msgid):
        """Dismiss specific notification"""
        # TODO: do it properly via builtin action
        n = self.notifications[msgid]
        del self.notifications[msgid]

        if n.persistent:
            storage_dir = self.storage_dirs['persistent']
        else:
            storage_dir = self.storage_dirs['volatile']

        filename = os.path.join(storage_dir, "{}.json".format(msgid))
        tmp_filename = os.path.join("/tmp", "{}.json".format(msgid))

        subprocess.call(["mv", filename, tmp_filename])
        subprocess.call(["rm", tmp_filename])
