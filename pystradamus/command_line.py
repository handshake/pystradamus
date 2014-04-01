#!/usr/bin/env python
import argparse
import logging
import sys

import pystradamus

def main():
    """Sets up the main config parser for the main entry point, this does common
    things like print help or the version and then dispatches to further down
    sub-parsers for specific information
    """
    # configure logging to just go to stdout
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-10s] (%(name)s) %(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )

    log = logging.getLogger(__name__)

    # build the main parser
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument('-c', '--config', metavar="FILE",
            type=argparse.FileType('r'), help="path to config file")
    main_parser.add_argument('-v', '--verbose', help="show debug messages",
            action='store_true')
    main_parser.add_argument('-d', '--database', metavar="FILE",
            help="path to the sqllite3 database file to use",
            default='evidence.db')
    main_parser.add_argument('--version', help='print version and exit')
    subparsers = main_parser.add_subparsers()

    #history functionality
    history_parser = subparsers.add_parser('history', help='history yo')
    history_parser.add_argument('-r', '--refresh', help="Pulls historic ticket "
            "data from jira", action="store_true")
    history_parser.add_argument('-p', '--predict', help="Generate a probability"
            " curve for the next assigned ticket with an estimate for a given "
            "user", action="store_true")
    history_parser.add_argument('username', type=str,
            help='JIRA username to query tickets for')
    history_parser.set_defaults(func=pystradamus.history.main)

    config_parser = subparsers.add_parser('config', help='config yo')
    config_parser.add_argument('-f', '--fields', action="store_true",
            help="Pulls custom fields and their ids from Jira")
    config_parser.set_defaults(func=pystradamus.config.main)

    # parse args and dispatch to the correct handler
    args = main_parser.parse_args()
    cfg = pystradamus.config.locate_and_parse(args.config)
    if cfg is None and args.func is not pystradamus.config.main:
        pystradamus.utils.error_exit("No configuration found!")
    args.cfg = cfg
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    pystradamus.storage.init(args.database)
    args.func(args)
