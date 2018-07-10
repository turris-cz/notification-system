#!/usr/bin/env python3

import argparse

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

    parser_list = subparsers.add_parser("list", help="List notification")
    # parser_list.add_argument("--id", help="ID of notification")
    parser_list.add_argument("plugins", help="List available plugins")

    return parser


def process_args(parser, api, args):
    """Call module interface based on args"""
    # not working yet
    if args.command == 'add':
        api.create(**vars(args))

    if args.command == 'list':
        if args.plugins:
            ret = api.get_plugins()

            print("Available plugins:")
            for k, v in ret.items():
                print(v)
    else:
        parser.print_usage()


def main():
    parser = create_argparser()
    args = parser.parse_args()

    api = Api()

    process_args(parser, api, args)


if __name__ == '__main__':
    main()
