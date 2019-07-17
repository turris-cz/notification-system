import glob
import os
import logging

from datetime import datetime
from pathlib import Path

from .exceptions import VersionMismatchError, NoSuchNotificationError
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

        self.paths = [
            Path(self.storage_dirs['volatile']),
            Path(self.storage_dirs['persistent']),
        ]

        self.latest_sync = [0 for _ in self.paths]
        self.sync()

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

    def load_new(self, pathstr):
        """Try to load new notification from file"""
        n = Notification.from_file(pathstr, self.plugin_storage)

        if n:
            self.notifications[n.notif_id] = n
            self.shortid_map[n.notif_id[:self.SHORTID_LENGTH]] = n.notif_id

    def _delete_from_memory(self, nid):
        """Remove notification that no longer exist on fs from in-memory cache."""
        del self.notifications[nid]
        del self.shortid_map[nid[:self.SHORTID_LENGTH]]

    def _update_notifications_from_fs(self):
        """Check for changes on hdd. Load new notifications
        Drop these that no longer exist.
        """
        if all(p.stat().st_mtime == l for p, l in zip(self.paths, self.latest_sync)):
                # nothing changed, we are in sync
                return

        notification_ids = {} 

        for path in self.paths:
            for p in path.glob('*.json'):
                notification_ids[p.stem] = p 
                
        # delete notifications than doesn't exits on fs anymore
        to_delete = self.notifications.keys() - notification_ids.keys()
        for nid in to_delete:
            self._delete_from_memory(nid)
        
        # load new notifications from fs
        to_delete_invalid = []
        to_add = notification_ids.keys() - self.notifications.keys()
        for nid in to_add:
            filepath = str(notification_ids[nid])
            try:
                self.load_new(filepath)
            except FileNotFoundError:
                continue
            except VersionMismatchError:
                logger.debug("Notification version mismatch - marking to delete")
                to_delete_invalid.append(filepath)
                continue
        
        # delete invalid notifications from fs
        for path in to_delete_invalid:
            self.remove_file(path)

    def valid_id(self, msgid):
        """Check if msgid is valid and message with that id exists"""
        # legacy compatibility
        # lookup by timestamp
        for nid, n in self.notifications.items():
            if msgid.isnumeric() and n.timestamp == int(msgid):
                return True

        if msgid not in self.notifications and msgid not in self.shortid_map:
            logger.debug("Notification ID '%s' does not exist", msgid)
            return False

        return True

    def _full_id(self, msgid):
        """
        Get full id of notification based on short id.
        Expects existing id.
        """
        # legacy compatibility
        # lookup by timestamp
        for nid, n in self.notifications.items():
            if msgid.isnumeric() and n.timestamp == int(msgid):
                return nid

        if len(msgid) == self.SHORTID_LENGTH:
            return self.shortid_map[msgid]

        return msgid

    def get(self, msgid):
        """Return single notification instance"""
        self.sync()

        if self.valid_id(msgid):
            msgid = self._full_id(msgid)

            return self.notifications[msgid]

        return None

    def _get_rendered(self, msgid, media_type, lang, force_media_type=False):
        """Return notification either cached or if missing, cache it and return"""
        msgid = self._full_id(msgid)
        n = self.notifications[msgid]

        mt = n.has_media_type(media_type)
        if not mt and force_media_type:
            return None

        return n.render(media_type, lang)

    def get_rendered(self, msgid, media_type, lang, force_media_type=False):
        """Get single notification rendered."""
        self.sync()

        if not self.valid_id(msgid):
            raise NoSuchNotificationError("Notification with ID '{}' does not exist".format(msgid))

        return self._get_rendered(msgid, media_type, lang, force_media_type)

    def get_all(self):
        """Get all stored notification objects"""
        self.sync()

        return self.notifications

    def get_all_rendered(self, media_type, lang):
        """Get all notifications rendered in lang and in given media_type"""
        self.sync()

        notifications = {}

        for msgid in self.notifications.keys():
            notifications[msgid] = self._get_rendered(msgid, media_type, lang)

        return notifications

    def sync(self):
        """
        Sync in-memory notifications with state on hdd.
        Delete old notifications and get new.
        """
        self._delete_invalid_messages()
        self._update_notifications_from_fs()
        
        self.latest_sync = [path.stat().st_mtime for path in self.paths]

    def _delete_invalid_messages(self):
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
        """
        Completely remove notification.
        Order of removal is important - remove file first and then instance in cache.
        """
        self.remove_from_fs(msgid)
        self.remove_from_cache(msgid)

    def remove_from_cache(self, msgid):
        """Remove single notification from in-memory cache"""
        if self.valid_id(msgid):
            msgid = self._full_id(msgid)

            del self.notifications[msgid]
            del self.shortid_map[msgid[:self.SHORTID_LENGTH]]

            logger.debug("Dismissing notification '%s'", msgid)

    def remove_from_fs(self, msgid):
        """Remove single notification file from FS"""
        if self.valid_id(msgid):
            msgid = self._full_id(msgid)
            n = self.notifications[msgid]

            if n.persistent:
                storage_dir = self.storage_dirs['persistent']
            else:
                storage_dir = self.storage_dirs['volatile']

            filepath = os.path.join(storage_dir, "{}.json".format(msgid))
            self._remove_file(filepath)

    def _remove_file(self, filepath):
        """Remove file from FS"""
        logger.debug("Removing file %s", filepath)

        try:
            os.unlink(filepath)
        except OSError as e:
            logger.error("Cannot remove file '%s'. Reason: %s", filepath, e)
            return
