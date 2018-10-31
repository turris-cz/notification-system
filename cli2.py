#!/usr/bin/env python3

import argparse
import json
import os
import sys

from notifylib.api import Api
from notifylib.exceptions import (
    MediaTypeNotAvailableException,
    NoSuchNotificationException,
)
from notifylib.sorting import Sorting

SEVERITIES = {
    'info': 'I',
    'warning': 'W',
    'error': 'E',
}

COLORS = {
    'info': '\033[34m',
    'warning': '\033[93m',
    'error': '\033[91m',
    'default': '\033[39m',
}


def create_argparser():
    """Create new argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Specify config file")

    subparsers = parser.add_subparsers(help="sub-command help", dest='command')

    parser_action = subparsers.add_parser("add", help="Add new notification")
    parser_action.add_argument("--template", help="Notification type / template", default='simple')
    parser_action.add_argument("--persistent", help="Persistent notification", action="store_true")
    parser_action.add_argument("--timeout", help="Timeout in minutes after which message disappear", type=int)
    parser_action.add_argument("--severity", help="Severity of message")
    parser_action.add_argument("--nodismiss", help="Disable explicit dismiss of message", action="store_false")
    parser_action.add_argument("--default-action", help="Set action which will be used as 'default'")

    group_add = parser_action.add_mutually_exclusive_group()
    group_add.add_argument('--from-json', metavar='JSON', help='Json string with template variables')
    group_add.add_argument('--from-env', metavar='ENV_VAR', help='ENV variable which will template variables be read from')

    parser_list = subparsers.add_parser("list", help="List various things")
    parser_list.add_argument("target", help="List stored messages or available templates", choices=["messages", "templates"], nargs="?", default="messages")
    parser_list.add_argument("--sort", help="Sort notifications by criterion", nargs="?")

    parser_get = subparsers.add_parser("get", help="Get specific message")
    parser_get.add_argument("msgid", help="ID of notification message")
    parser_get.add_argument("media_type", help="Media type of notification message", nargs="?", default="simple")
    parser_get.add_argument("lang", help="Language of notification message", nargs="?", default="en")
    parser_get.add_argument("--force-media-type", dest="force_media_type", help="Request media type and don't return default media type in case requested one is not available", action="store_true")

    parser_call = subparsers.add_parser("call", help="Call actions on messages")
    parser_call.add_argument("msgid", help="ID of notification message")
    parser_call.add_argument("action", help="Name of action")

    return parser


def print_severity(severity):
    return "{}[{}]{}".format(COLORS[severity], SEVERITIES[severity], COLORS['default'])


def print_templates(templates):
    """Pretty print templates list"""
    print("Available templates:")
    for t in templates:
        print(t)


def print_notifications(notifications):
    """Pretty print stored notifications"""
    print("Stored notifications:")
    for k, v in notifications.items():
        trimmed = ' '.join(v['message'][:80].split())
        severity = v['metadata']['severity']

        print("{} {}\t{}".format(print_severity(severity), k, trimmed))


def print_notification(notification):
    """Print single rendered notification"""
    print("Message: {}".format(notification['message']))
    print("Actions: {}".format(notification['actions']))
    print("Metadata: {}".format(notification['metadata']))


def process_args(parser, args):
    """Call module interface based on args"""
    if args.config:
        api = Api(os.path.abspath(args.config))
    else:
        api = Api()

    if args.command == 'add':
        opts = {
            'skel_id': args.template,
            'data': json.loads(args.from_json),
        }

        if args.persistent:
            opts['persistent'] = args.persistent
        if args.severity:
            opts['severity'] = args.severity
        if args.timeout:
            opts['timeout'] = args.timeout * 60
        if not args.nodismiss:
            opts['explicit_dismiss'] = args.nodismiss
        if args.default_action:
            opts['default_action'] = args.default_action

        ret = api.create(**opts)

        if ret:
            print("Succesfully created notification '{}'".format(ret))
        else:
            print("Failed to create notification. Please see the log for more details.")
            sys.exit(1)

    elif args.command == 'list':
        if args.target == 'messages':
            ret = api.get_notifications()

            if args.sort:
                ret = Sorting.sort_by(ret, args.sort)

            print_notifications(ret)

        elif args.target == 'templates':
            ret = api.get_templates()
            print_templates(ret)

    elif args.command == 'get':
        msgid = args.msgid
        media_type = args.media_type
        lang = args.lang

        try:
            ret = api.get_rendered_notification(msgid, media_type, lang, args.force_media_type)

            print_notification(ret)
        except NoSuchNotificationException as e:
            print(e)
        except MediaTypeNotAvailableException as e:
            print(e)
    elif args.command == 'call':
        api.call_action(args.msgid, args.action)
    else:
        parser.print_usage()


def main():
    parser = create_argparser()
    args = parser.parse_args()

    process_args(parser, args)


if __name__ == '__main__':
    main()
