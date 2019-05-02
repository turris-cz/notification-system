"""Backward compatible interface as list_notifications replacement"""

import argparse
import json

from notifylib import Api
from .severity import Severity


def reformat(notifications, indent=True):
    out = {
        'notifications': []
    }

    for v in notifications.values():
        notification = {
            'displayed': False,
            'id': f"{v['metadata']['timestamp']}-100000",
            # 100000 is there because acording to json schema
            # foris expects some numbers in form [1-9][0-9]*
            # also old notifications id contained six digits
            'severity': Severity.standard_to_legacy(v['metadata']['severity']),
            'messages': {
                'en': v['message'],
            }
        }

        out['notifications'].append(notification)

    if indent:
        return json.dumps(out, indent=4)
    else:
        return json.dumps(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", action="store_true", default=False, help="Compact listing of notifications")

    args = parser.parse_args()

    api = Api()
    notifications = api.get_notifications()

    print(reformat(notifications, indent=not args.n))


if __name__ == "__main__":
    main()
