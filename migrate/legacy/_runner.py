"""
Package API is defined here.
"""
import time
import os
import json
import fnmatch
import sys
import itertools
from importlib import util as import_util

MIGRATIONS_DIR = 'migrations/'
STATE_FILE = MIGRATIONS_DIR + '.state'
DIRECTION_UP = 'up'
DIRECTION_DOWN = 'down'


def create(
        name: str,
        migrations_dir: str = MIGRATIONS_DIR,
        template_file: str = None) -> None:
    """
    Create new migration file named
    {timestamp}_{name}.py

    :param name: will be part of created file name
    :param migrations_dir: file destination
    :param template_file: contents of file to be created
    :return: None
    """
    if template_file is None:
        template = """\
def up():
    pass


def down():
    pass
"""
    else:
        with open(template_file, 'r') as file:
            template = file.read()

    migrations_dir = (
        lambda path: path if path[-1] == '/' else path + '/'
    )(migrations_dir)

    os.makedirs(migrations_dir, 0o775, exist_ok=True)
    filename = '{path}{time:.0f}_{name}.py'.format(
        path=migrations_dir,
        time=time.time(),
        name=name.replace(' ', '_')
    )
    with open(filename, 'w') as file:
        file.write(template)
    print('File \'{}\' has been created.'.format(filename))


def perform(
        direction: str = DIRECTION_UP,
        target: str = None,
        migrations_dir: str = MIGRATIONS_DIR,
        state_file: str = STATE_FILE) -> None:
    """
    Read current database state, apply (or revert) specified
    migrations, and update the state.

    :param direction: 'up' or 'down'
    :param target: name of last migration which wil be performed
        (or reverted) or number of migrations to perform
    :param migrations_dir: location of migration files
    :param state_file: path to state file
    :return: None
    """

    if direction != DIRECTION_UP and direction != DIRECTION_DOWN:
        raise MigrationError('direction {} is invalid.'.format(direction))

    if isinstance(target, str) and target.isdecimal():
        number = int(target)
        if number > 0:
            target = number

    migrations_dir = (
        lambda path: path if path[-1] == '/' else path + '/'
    )(migrations_dir)

    available = get_all_migrations(migrations_dir)
    performed = get_performed_migrations(state_file)
    check_integrity(available, performed)
    migrations = get_migrations(available, performed, direction, target)

    def run_and_show_time():
        for migration in migrations:
            yield run(migration, migrations_dir, direction)

    sys.path.insert(0, os.getcwd())
    total_time = sum(
        run_and_show_time()
    )
    del sys.path[0]

    set_state(direction, performed, migrations, state_file)

    print('\nMigrations have been {action}. Total time: {time:.3f}s'.format(
        action='reverted' if direction == DIRECTION_DOWN else 'applied',
        time=total_time
    ))


def show(
        migrations_dir: str = MIGRATIONS_DIR,
        state_file: str = STATE_FILE) -> None:
    """
    Print current database state to stdout.

    :param migrations_dir: location of migration files
    :param state_file: path to state file
    :return: None
    """
    performed_header = 'Applied migrations:'
    new_header = 'New migrations:'
    available_header = 'Available migrations:'

    def format_list(items, header):
        return '\n'.join([
            '-' * len(header),
            header,
            '-' * len(header),
            '\n'.join(items),
        ]) if items else ''

    performed = get_performed_migrations(state_file)
    available = get_all_migrations(migrations_dir)
    try:
        check_integrity(available, performed)
    except MigrationError as e:
        info = e.args[1]
        performed_str = format_list(performed, performed_header)
        available_str = format_list(available, available_header)
        raise MigrationError('\n'.join([
            info,
            performed_str,
            available_str,
        ])) from e

    new = available[len(performed):]
    performed_str = format_list(performed, performed_header)
    new_str = format_list(new, new_header)
    if performed_str and new_str:
        print(performed_str + '\n' + new_str)
    else:
        print(performed_str + new_str)


def get_all_migrations(migrations_dir):
    try:
        available = [
            file
            for file in os.listdir(migrations_dir)
            if fnmatch.fnmatch(file, '*.py')
        ]
        available.sort()
        return available
    except FileNotFoundError as e:
        raise MigrationError('no migrations found.') from e


def get_performed_migrations(state_file):
    try:
        with open(state_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def check_integrity(available, performed):
    for available_item, performed_item in itertools.zip_longest(
            available, performed
    ):
        if available_item != performed_item and performed_item is not None:
            break
    else:
        return

    info = """\
migration order is corrupt.
Expected '{performed}' in the directory.
Got '{available}' instead.
You must resolve the conflict manually."""
    info = info.format(performed=performed_item, available=available_item)
    raise MigrationError(info + '\nFor more info run `migrate show`.', info)


def get_migrations(available, performed, direction, target):
    if direction == DIRECTION_DOWN:
        migrations = performed.copy()
        migrations.reverse()
    else:
        migrations = available[len(performed):]

    if target is None:
        if direction == DIRECTION_DOWN:
            return migrations[:1]
        return migrations
    if isinstance(target, int):
        migrations = migrations[:target]
    else:
        for index, migration in enumerate(migrations):
            if migration == target:
                break
        else:
            raise MigrationError(
                'migration with provided name {} not found.'.format(target)
            )
        migrations = migrations[:index + 1]

    return migrations


def run(name, directory, direction):
    import_spec = import_util.spec_from_file_location(
        name,
        directory + name
    )
    module = import_util.module_from_spec(import_spec)
    import_spec.loader.exec_module(module)

    print('{action} {name}...'.format(
        action='Reverting' if direction == DIRECTION_DOWN else 'Applying',
        name=name,
    ), end='', flush=True)

    action = getattr(module, direction)
    started = time.time()
    action()
    duration = time.time() - started

    print('done (time: {:.3f}s)'.format(duration))
    return duration


def set_state(direction, old_state, migrations, state_file):
    if direction == DIRECTION_DOWN:
        state = old_state[:-len(migrations)]
    else:
        state = old_state + migrations
    with open(state_file, 'w') as file:
        json.dump(
            state,
            file,
            indent=2
        )


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
