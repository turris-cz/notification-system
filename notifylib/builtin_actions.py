from .helpers import remove


def reboot():
    """Reboot device"""
    print("Rebooting")


def dismiss(id):
    """Dismiss message -> delete it"""
    print("Dismissing msg id {}".format(id))
    remove(id)
