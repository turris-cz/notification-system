import os
import subprocess

from datetime import datetime

from .logger import logger
from .notification import Notification


class NotificationStorage:
    """In-memory notification storage that serialize and deserialize them"""

    def __init__(self, volatile_dir, persistent_dir):
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

        Serializate to disk
        Render fallback in default languages
        """
        self.notifications[n.notif_id] = n

        if n.persistent:
            storage_dir = self.storage_dirs['persistent']
        else:
            storage_dir = self.storage_dirs['volatile']

        json_data = n.serialize()

        # save to disk
        file_path = os.path.join(storage_dir, "{}.json".format(n.notif_id))

        try:
            with open(file_path, 'w') as f:
                f.write(json_data)
        except OSError:
            logger.error("Error during writing notification to disk!")

    def load(self, storage_dir):
        """Deserialize all notifications from FS"""
        logger.debug("Deserializing notifications from '%s'", storage_dir)
        for _, _, files in os.walk(storage_dir):
            for f in files:
                filepath = os.path.join(storage_dir, f)
                logger.debug("File %s", filepath)

                n = Notification.from_file(filepath)

                if n:
                    self.notifications[n.notif_id] = n

    def get(self, msgid):
        """Return single notification instance"""
        return self.notifications[msgid]

    def get_rendered(self, msgid, media_type, lang):
        """Return notification either cached or if missing, cache it and return"""
        if (msgid, media_type, lang) not in self.rendered:
            self.rendered[(msgid, media_type, lang)] = self.notifications[msgid].render(media_type, lang)

        return self.rendered[(msgid, media_type, lang)]

    def get_all(self):
        """Get all stored notification objects"""
        return self.notifications

    def filter_rendered(self, media_type, lang):
        """Filter rendered notifications by lang and media_type"""
        result = {}

        for k, v in self.rendered.items():
            if k[1] == media_type and k[2] == lang:
                result[k[0]] = v

        return result

    def get_all_rendered(self, media_type, lang):
        """Get all notifications rendered in lang and in given media_type"""
        # expand notification keys to triples
        expanded_keys = []
        for k in self.notifications.keys():
            expanded_keys.append((k, media_type, lang))

        # render only uncached notifications
        cached = set(self.rendered.keys())
        for k in expanded_keys:
            if k not in cached:
                self.get_rendered(*k)

        # return notifications only in desired media_type and lang
        return self.filter_rendered(media_type, lang)

    def delete_invalid_messages(self):
        """Delete messages based on their timeout"""
        to_delete = []
        now = datetime.utcnow()

        for n in self.notifications.values():
            if not n.is_valid(now):
                to_delete.append(n)

        for n in to_delete:
            self.remove(n.notif_id)
            logger.debug("Deleting notification '%s' due to timeout", n.notif_id)

    def remove(self, msgid):
        """Remove single notification"""
        n = self.notifications[msgid]
        del self.notifications[msgid]

        logger.debug("Dismissing notification '%s'", msgid)
        if n.persistent:
            storage_dir = self.storage_dirs['persistent']
        else:
            storage_dir = self.storage_dirs['volatile']

        filename = os.path.join(storage_dir, "{}.json".format(msgid))
        tmp_filename = os.path.join("/tmp", "{}.json".format(msgid))

        subprocess.call(["mv", filename, tmp_filename])
        subprocess.call(["rm", tmp_filename])
