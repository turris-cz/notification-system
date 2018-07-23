#!/usr/bin/env python3

import argparse
import os

from notifylib.api import Api

"""
Interface:
* list <id>
* list (all)
* create <template, message, **params>
* dismiss <id>
* action <id, action_name>
* available notifications
* available media types <template_name>??
* available actions of plugin <name>
* show complete message as media type (type)
"""


def create_argparser():
    """Create new argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Specify config file")

    subparsers = parser.add_subparsers(help="sub-command help", dest='command')

    parser_action = subparsers.add_parser("add", help="Add new notification")
    parser_action.add_argument("message", help="Notification message")
    parser_action.add_argument("-t", "--template", help="Notification type / template", default='simple')
    parser_action.add_argument("--persistent", help="Persistent notification (default: false)", action="store_true")

    parser_list = subparsers.add_parser("list", help="List notification")
    parser_list.add_argument("target", help="List multiple things o your choice", choices=["all", "plugins", "templates"], nargs="?", default="all")
    # parser_list.add_argument("--id", help="ID of notification")

    return parser


def print_plugins(plugins):
    """Pretty print plugin list"""
    print("Available plugins:")
    for p in plugins:
        print(p)


def print_templates(templates):
    """Pretty print templates list"""
    print("Available templates:")
    for t in templates:
        print(t)


def print_notifications(notifications):
    """Pretty print stored notifications"""
    print("Stored notifications")
    for k, v in notifications.items():
        print("{} - {}".format(k, v))


def process_args(parser, args):
    """Call module interface based on args"""
    if args.config:
        api = Api(os.path.abspath(args.config))
    else:
        api = Api()

    if args.command == 'add':
        api.create(**vars(args))

    elif args.command == 'list':
        if args.target == 'all':
            ret = api.get_notifications()
            print_notifications(ret)
        elif args.target == 'plugins':
            ret = api.list_plugins()
            print_plugins(ret)

        elif args.target == 'templates':
            ret = api.get_templates()
            print_templates(ret)
    else:
        parser.print_usage()


def main():
    parser = create_argparser()
    args = parser.parse_args()

    process_args(parser, args)


if __name__ == '__main__':
    main()
