"""Backward compatible interface for user-notify-display"""

import argparse

from . import Api


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", help="List of ids to mark as diplayed", nargs="*")

    args = parser.parse_args()

    api = Api()

    for instance in args.ids:
        nid = instance.split('-')[0]
        api.call_action(nid, 'dismiss')


if __name__ == '__main__':
    main()
