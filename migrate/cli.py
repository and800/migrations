#!/usr/bin/env python3
"""
CLI frontend for package API.
"""
import sys
import argparse
from . import _runner, __version__


def entrypoint(argv=sys.argv[1:]):
    """
    Parse arguments and perform appropriate action.
    Wrap it into `sys.exit()` call.

    :param argv: list of arguments
    :return: status code 0 if succeeded or exception object if failed
    """
    parser = _configure_parser()
    args = vars(parser.parse_args(argv))

    if 'action' not in args:
        args['action'] = 'up'
    try:
        if args['action'] == 'create':
            method_args = _transform_args(args, [
                'name',
                'migrations_dir',
                'template_file',
            ])
            _runner.create(**method_args)
        elif args['action'] == 'show':
            method_args = _transform_args(args, [
                'migrations_dir',
                'template_file',
            ])
            _runner.show(**method_args)
        else:
            method_args = _transform_args(args, [
                ('action', 'direction'),
                'target',
                'migrations_dir',
                'state_file',
            ])
            _runner.perform(**method_args)
        return 0
    except _runner.MigrationError as e:
        return e


def _configure_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    parser.add_argument(
        '-v', '--version',
        help='show version and exit',
        action='version',
        version='migrations v' + __version__,
    )

    parser.add_argument(
        '-d', '--migrations-dir',
        help='directory where migrations are stored'
    )
    parser.add_argument(
        '-s', '--state-file',
        help='location of file which stores database state'
    )
    parser.add_argument(
        '-t', '--template-file',
        help='location of template file for new migrations'
    )

    subparsers = parser.add_subparsers()

    action_create = subparsers.add_parser('create')
    action_create.add_argument(
        'name',
        help='name of new migration file'
    )
    action_create.set_defaults(action='create')

    action_show = subparsers.add_parser('show')
    action_show.set_defaults(action='show')

    action_up = subparsers.add_parser('up')
    action_up.add_argument(
        'target', nargs='?',
        help='name of the last migration or number of migrations '
             '(by default perform all available)'
    )
    action_up.set_defaults(action='up')

    action_down = subparsers.add_parser('down')
    action_down.add_argument(
        'target', nargs='?',
        help='name of the last migration or number of migrations '
             '(by default revert one)'
    )
    action_down.set_defaults(action='down')

    return parser


def _transform_args(args, required):
    result = {}
    for required_arg in required:
        if isinstance(required_arg, tuple):
            old_key, key = required_arg
        else:  # type(required_arg) == str
            old_key = key = required_arg
        try:
            value = args[old_key]
        except KeyError:
            value = None
        if value is not None:
            result[key] = value
    return result


if __name__ == '__main__':
    sys.exit(entrypoint())
