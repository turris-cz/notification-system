import glob
import os
import logging

from datetime import datetime
from functools import lru_cache

from .exceptions import VersionMismatchException
from .notification import Notification

logger = logging.getLogger(__name__)


class NotificationStorage:
    """In-memory notification storage that serialize and deserialize them"""
    SHORTID_LENGTH = 8

    def __init__(self, volatile_dir, persistent_dir, plugin_storage):
        self.storage_dirs = {
            'persistent': persistent_dir,
            'volatile': volatile_dir,
        }
        self.plugin_storage = plugin_storage

        self.notifications = {}
        self.shortid_map = {}

        self.load(volatile_dir)
        self.load(persistent_dir)

    def store(self, n):
        """
        Store in memory

        Serializate to disk
        Render fallback in default languages
        """
        self.notifications[n.notif_id] = n
        self.shortid_map[n.notif_id[:self.SHORTID_LENGTH]] = n.notif_id

        if n.persistent:
            storage_dir = self.storage_dirs['persistent']
        else:
            storage_dir = self.storage_dirs['volatile']

        # save to disk
        file_path = os.path.join(storage_dir, "{}.json".format(n.notif_id))

        try:
            with open(file_path, 'w') as f:
                f.write(n.serialize())
        except OSError:
            logger.error("Error during writing notification to disk!")
            return False

        return True

    def load(self, storage_dir):
        """Deserialize all notifications from FS"""
        logger.debug("Deserializing notifications from '%s'", storage_dir)
        to_delete = []

        for filepath in glob.glob(os.path.join(storage_dir, '*.json')):
            try:
                n = Notification.from_file(filepath, self.plugin_storage)

                if n:
                    self.notifications[n.notif_id] = n
                    self.shortid_map[n.notif_id[:self.SHORTID_LENGTH]] = n.notif_id
            except VersionMismatchException:
                logger.debug("Notification version mismatch - marking to delete")
                to_delete.append(filepath)
                continue

        for path in to_delete:
            self.remove_file(path)

    def valid_id(self, msgid):
        """Check if msgid is valid and message with that id exists"""
        if msgid not in self.notifications and msgid not in self.shortid_map:
            logger.debug("Notification ID '%s' does not exist", msgid)
            return False

        return True

    def _full_id(self, msgid):
        """Get full id of notification based on short id"""
        if len(msgid) == self.SHORTID_LENGTH:
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
        notifications = {}

        for msgid in self.notifications.keys():
            notifications[msgid] = self.get_rendered(msgid, media_type, lang)

        return notifications

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
            del self.shortid_map[msgid[:self.SHORTID_LENGTH]]

            logger.debug("Dismissing notification '%s'", msgid)
            if n.persistent:
                storage_dir = self.storage_dirs['persistent']
            else:
                storage_dir = self.storage_dirs['volatile']

            filepath = os.path.join(storage_dir, "{}.json".format(msgid))
            self.remove_file(filepath)

    def remove_file(self, filepath):
        """Remove file from FS"""
        logger.debug("Removing file %s", filepath)
        tmp_filepath = "{}.tmp".format(filepath)
        try:
            os.rename(filepath, tmp_filepath)
        except FileNotFoundError as e:
            logger.error(e)
            return
        except IsADirectoryError:
            logger.error("Cannot rename file. There already is a directory with the same name!")
            return

        try:
            os.unlink(tmp_filepath)
        except OSError as e:
            logger.error("Cannot remove tempfile '%s'. Reason: %s", tmp_filepath, e)
            return
