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
    parser.add_argument("-c", "--config", help="Specify config file")

    subparsers = parser.add_subparsers(help="sub-command help", dest='command')

    parser_action = subparsers.add_parser("add", help="Add new notification")
    parser_action.add_argument("message", help="Notification message")
    parser_action.add_argument("--persistent", help="Persistent notification (default: false)", action="store_true")

    subparsers.add_parser("list", help="List notification")

    parser_dismiss = subparsers.add_parser("dismiss", help="Dismiss notification")
    parser_dismiss.add_argument("id", help="ID of notification")

    args = parser.parse_args()

    if (args.config):
        print("Using custom config {:s}".format(args.config))
        lib.set_config(args.config)

    # handle commands
    if args.command == 'add':
        if args.persistent:
            lib.add(args.message, persistent=True)
        else:
            lib.add(args.message)
    elif args.command == 'list':
        lib.list_all()
    elif args.command == 'dismiss':
        lib.call('dismiss', id=args.id)
    else:
        print(parser.print_help())


if __name__ == "__main__":
    main()
