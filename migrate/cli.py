import argparse
import sys
import os
from . import runner


def entrypoint():
    sys.path.insert(0, os.getcwd())

    parser = _configure_parser()
    args = vars(parser.parse_args())

    if args['action'] == 'create':
        if args['spec'] is None:
            raise Exception('name is not set')
        method_args = _transform_args(args, {
            'spec': 'name',
            'migrations_dir': 'migrations_dir',
            'template_file': 'template_file',
        })
        runner.create(**method_args)
    else:
        method_args = _transform_args(args, {
            'action': 'direction',
            'spec': 'target',
            'migrations_dir': 'migrations_dir',
            'state_file': 'state_file',
        })
        runner.perform(**method_args)


def _configure_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

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
        help='location of template file for ner migrations'
    )

    parser.add_argument(
        'action',
        choices=['up', 'down', 'create'],
        help='action',
        nargs='?',
        default='up',
    )
    parser.add_argument('spec', nargs='?', help='action specification')

    return parser


# def _transform_args(args, mapping):
#     result = {}
#     for key, arg in args.items():
#         if arg is None:
#             continue
#         try:
#             key = mapping[key]
#         except KeyError:
#             pass
#         result[key] = arg
#     return result


def _transform_args(args, mapping):
    result = {}
    for then, now in mapping.items():
        arg = args[then]
        if arg is not None:
            result[now] = arg
    return result
