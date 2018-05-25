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
    parser_action.add_argument("--action", help="Action used withing notification", default="dismiss")
    parser_action.add_argument("--persistent", help="Persistent notification (default: false)", action="store_true")
    parser_action.add_argument("--severity", help="Notification message", default="info")
    parser_action.add_argument("--timeout", help="Message timeout in seconds", type=int)

    parser_list = subparsers.add_parser("list", help="List notification")
    parser_list.add_argument("--id", help="ID of notification")

    parser_dismiss = subparsers.add_parser("dismiss", help="Dismiss notification")
    parser_dismiss.add_argument("id", help="ID of notification")

    args = parser.parse_args()

    if (args.config):
        print("Using custom config {:s}".format(args.config))
        lib.set_config(args.config)

    # handle commands
    if args.command == 'add':
        lib.add(**vars(args))
    elif args.command == 'list':
        if args.id:
            lib.list(args.id)
        else:
            lib.list_all()
    elif args.command == 'dismiss':
        lib.call('dismiss', id=args.id)
    else:
        print(parser.print_help())


if __name__ == "__main__":
    main()
