"""Backward compatible interface as create_notification replacement"""

import argparse

from notifylib import Api

# Translation table for legacy severity levels
SEVERITY_LEVELS = {
    'restart': 'action_needed',
    'error': 'error',
    'update': 'info',
    'news': 'announcement',
}


def create_argparser():
    parser = argparse.ArgumentParser(
        epilog="Note: This compatibility wrapper is not 100% compatible with original script behaviour. Notifications are always returned in English due to different implementation.")
    parser.add_argument("-t", action="store_true", help="Pushes the notification via email right away (not implemented yet)")
    parser.add_argument("-s", choices=['restart', 'error', 'update', 'news'], help="Severity of message", required=True)
    parser.add_argument(
        "lang_one",
        help="Mandatory message. Czech is expected here, however if you don't specifify lang_two, lang_one is considered as English"
    )
    parser.add_argument("lang_two", nargs="?", help="Message in English")

    return parser


def process_args(parser, args):
    severity = SEVERITY_LEVELS[args.s]

    if args.lang_two:
        data = {'message': args.lang_two}
    else:
        data = {'message': args.lang_one}

    opts = {
        'skel_id': 'simple.empty',
        'data': data,
        'severity': severity,
    }

    api = Api()
    api.create(**opts)


def main():
    parser = create_argparser()
    args = parser.parse_args()

    process_args(parser, args)


if __name__ == "__main__":
    main()
