"""
Miscellaneous useful stuff.
"""
import re
from types import ModuleType
from importlib import util as import_util


class MigrationError(Exception):
    """
    Exceptions for all user errors. Any such an error
    is formatted and printed to stderr.
    """
    def __init__(self, message, *args):
        super(MigrationError, self).__init__(message, *args)
        self.message = message

    def __str__(self):
        return 'Error: {}'.format(self.message)


def import_from_file(file: str, name: str = None) -> ModuleType:
    """
    Find module on given path, load it and return it.
    :param file: module location
    :param name: module name
    :return: loaded module
    """
    if name is None:
        try:
            name = re.search('([^/]+)\.py', file).group(1)
        except (AttributeError, IndexError):
            name = 'default'

    spec = import_util.spec_from_file_location(
        name,
        file
    )
    module = import_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
