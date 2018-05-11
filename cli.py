#!/usr/bin/env python3

import argparse

from notifylib import lib

"""
interface:
<cli> add <msg>
<cli> list
<cli> dismiss <id>
"""


def main():
    # parse args
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="sub-command help", dest='command')

    parser_action = subparsers.add_parser("add", help="Add new notification")
    parser_action.add_argument("message", help="Notification message")

    parser_list = subparsers.add_parser("list", help="List notification")

    parser_dismiss = subparsers.add_parser("dismiss", help="Dismiss notification")
    parser_dismiss.add_argument("id", help="ID of notification")

    args = parser.parse_args()

    if args.command == 'add':
        lib.add(args.message)
    elif args.command == 'list':
        lib.list_all()
    elif args.command == 'dismiss':
        lib.call('dismiss', id=args.id)


if __name__ == "__main__":
    main()
