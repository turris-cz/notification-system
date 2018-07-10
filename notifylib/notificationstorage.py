class NotificationStorage:
    """In-memory notification storage that serialize and deserialize them"""
    def __init__(self, volatile_dir, persistent_dir, notification_types):
        print("Constructing new NotifyStorage")
        self.init_logger()
        self.load(volatile_dir)
        self.load(persistent_dir)

        self.notification_types = notification_types  # notification data types/templates
        self.notifications = []
        # self.cached = {}

    def init_logger(self):
        pass

    def store(self, n):
        """Store in memory and serializate to disk"""
        self.notifications.append(n)
        self.serialize(n)

    # TODO: WIP
    #def store_persistent(self, n):
    #    self.serialize(n, self.storage_dirs['persistent'])

    #def store_volatile(self, n):
    #    self.serialize(n, self.storage_dirs['volatile'])

    #def serialize(self, n, destination):
    #    """Serialize notification to disk"""
    #    # save metadata to FS
    #    # render fallback form
    #    pass

    def load(self, storage_dir):
        """Deserialize from FS"""

        # for f in ls storage_dir:
        #   n = NotificationType.from_file(f)
        #   if not n.valid():
        #       delete_from_fs()

    # TODO: find better key to identify notification instance in dict
    def get_skeleton(self, name):
        """Return notification instance with filled in mandatory attributes"""
        return self.notification_types[name].create_instance()

    # TODO: find better key to identify notification instance in dict
    def get_notification(self, name):
        """Return notification either cached or if missing, cache it and return"""
        if not self.cached[name]:
            # do something to create/cache
            # do it inside serialization
            pass
        return self.cached[name]

    def get_notification_types(self):
        """Return all notification types"""
        return self.notification_types

    # TODO: WIP helper fce
    def render_one(self, notif):
        pass

    def render_all(self):
        """Render all notifications"""
        for n in self.notifications:
            self.render_one(n)
