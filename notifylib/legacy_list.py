"""Backward compatible interface as list_notifications replacement"""

import argparse
import json

from notifylib import Api

# Translation table for legacy severity levels
SEVERITY_LEVELS = {
    'action_needed': 'restart',
    'error': 'error',
    'info': 'update',
    'announcement': 'news',
}


def reformat(notifications, indent=True):
    out = {
        'notifications': []
    }

    for v in notifications.values():
        notification = {
            'displayed': False,
            'id': f"{v['metadata']['timestamp']}-000000",
            # 00000 is there because foris expects some numbers there
            'severity': SEVERITY_LEVELS[v['metadata']['severity']],
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
