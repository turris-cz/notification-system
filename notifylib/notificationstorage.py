import os

from collections import OrderedDict
from datetime import datetime
from functools import lru_cache

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
        self.shortid_map = {}

        self.load(volatile_dir)
        self.load(persistent_dir)
        self._sort_notifications(self.notifications)

    def store(self, n):
        """
        Store in memory

        Serializate to disk
        Render fallback in default languages
        """
        self.notifications[n.notif_id] = n
        self.shortid_map[n.notif_id[-5:]] = n.notif_id

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
                    self.shortid_map[n.notif_id[-5:]] = n.notif_id

    def _sort_notifications(self, dictionary):
        """Sort notifications after load to maintain time-based order"""
        self.notifications = OrderedDict(sorted(dictionary.items(), key=lambda kv: kv[0]))

    def valid_id(self, msgid):
        """Check if msgid is valid and message with that id exists"""
        if len(msgid) != 5 and len(msgid) != 16:
            logger.warning("Notification id is invalid - incorrect format")
            return False

        # TODO: regex check for correct format?

        if msgid not in self.notifications and msgid not in self.shortid_map:
            logger.warning("Notification id is invalid - notification does not exist")
            return False

        return True

    def _full_id(self, msgid):
        """Get full id of notification based on short id"""
        if len(msgid) == 5:
            return self.shortid_map[msgid]

        return msgid

    def get(self, msgid):
        """Return single notification instance"""
        if self.valid_id(msgid):
            msgid = self._full_id(msgid)

            return self.notifications[msgid]

        return None

    @lru_cache(maxsize=256)
    def get_rendered(self, msgid, media_type, lang, force_media_type=False):
        """Return notification either cached or if missing, cache it and return"""
        msgid = self._full_id(msgid)
        n = self.notifications[msgid]

        mt = n.has_media_type(media_type)
        if not mt and force_media_type:
            return None

        return n.render(media_type, lang)

    def get_all(self):
        """Get all stored notification objects"""
        return self.notifications

    def get_all_rendered(self, media_type, lang):
        """Get all notifications rendered in lang and in given media_type"""
        od = OrderedDict()

        for msgid in self.notifications.keys():
            od[msgid] = self.get_rendered(msgid, media_type, lang)

        return od

    def delete_invalid_messages(self):
        """Delete messages based on their timeout"""
        to_delete = []
        now = datetime.utcnow()

        for n in self.notifications.values():
            if not n.is_valid(now):
                to_delete.append(n)

        for n in to_delete:
            logger.debug("Deleting notification '%s' due to timeout", n.notif_id)
            self.remove(n.notif_id)

    def remove(self, msgid):
        """Remove single notification"""
        if self.valid_id(msgid):
            msgid = self._full_id(msgid)
            n = self.notifications[msgid]

            del self.notifications[msgid]
            del self.shortid_map[msgid[-5:]]

            logger.debug("Dismissing notification '%s'", msgid)
            if n.persistent:
                storage_dir = self.storage_dirs['persistent']
            else:
                storage_dir = self.storage_dirs['volatile']

            filename = os.path.join(storage_dir, "{}.json".format(msgid))
            tmp_filename = os.path.join("/tmp", "{}.json".format(msgid))

            # TODO: figure out how to pass what exactly failed to user

            try:
                os.rename(filename, tmp_filename)
            except FileNotFoundError as e:
                logger.error(e)
                return
            except IsADirectoryError:
                logger.error("Cannot rename file. There already is a directory with the same name!")
                return

            try:
                os.unlink(tmp_filename)
            except OSError as e:
                logger.error("Cannot remove tempfile '%s'. Reason: %s", tmp_filename, e)
                return
