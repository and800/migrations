import time
import os
import json
import fnmatch
import sys
import itertools
from importlib import util as import_util

migrations_dir_ = 'migrations/'
state_file_ = migrations_dir_ + '.state'


def create(name, migrations_dir=migrations_dir_, template_file=None):
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
    with open('{path}{time}_{name}.py'.format(
        path=migrations_dir,
        time=str(int(time.time())),
        name=name.replace(' ', '_')
    ), 'w') as file:
        file.write(template)


def perform(
        direction='up',
        target=None,
        migrations_dir=migrations_dir_,
        state_file=state_file_):

    if direction != 'up' and direction != 'down':
        raise MigrationError('direction {} is invalid'.format(direction))

    if isinstance(target, str) and target.isdecimal():
        number = int(target)
        if number > 0:
            target = number

    migrations_dir = (
        lambda path: path if path[-1] == '/' else path + '/'
    )(migrations_dir)

    available = get_all_migrations(migrations_dir)
    performed = get_performed_migrations(state_file)
    migrations = get_migrations(available, performed, direction, target)

    sys.path.insert(0, os.getcwd())
    for migration in migrations:
        run(migration, migrations_dir, direction)
    del sys.path[0]

    set_state(direction, performed, migrations, state_file)


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
        raise MigrationError('no migrations found') from e


def get_performed_migrations(state_file):
    try:
        with open(state_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def get_migrations(available, performed, direction, target):

    for available_item, performed_item in itertools.zip_longest(
        available, performed
    ):
        if available_item != performed_item and performed_item is not None:
            raise MigrationError('migration order is corrupt')

    if direction == 'down':
        migrations = performed.copy()
        migrations.reverse()
    else:
        migrations = available[len(performed):]

    if target is None:
        if direction == 'down':
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
                'migration with provided name {} not found'.format(target)
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

    getattr(module, direction)()


def set_state(direction, old_state, migrations, state_file):
    if direction == 'down':
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
    def __init__(self, message, *args):
        super(MigrationError, self).__init__(message, *args)
        self.message = message

    def __str__(self):
        return 'Error: {}.'.format(self.message)
