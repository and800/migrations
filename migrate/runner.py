import time
import os
import json
import fnmatch
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
        raise _MigrationError('direction {} is invalid'.format(direction))

    if isinstance(target, str) and target.isdecimal():
        number = int(target)
        if number > 0:
            target = number

    available = _get_all_migrations(migrations_dir)
    performed = _get_performed_migrations(state_file)
    migrations = _get_migrations(available, performed, direction, target)

    for migration in migrations:
        _run(migration, migrations_dir, direction)

    _set_state(direction, performed, migrations, state_file)


def _get_all_migrations(migrations_dir):
    try:
        available = [
            file
            for file in os.listdir(migrations_dir)
            if fnmatch.fnmatch(file, '*.py')
        ]
        available.sort()
        return available
    except FileNotFoundError as e:
        raise _MigrationError('no migrations found') from e


def _get_performed_migrations(state_file):
    try:
        with open(state_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def _get_migrations(available, performed, direction, target):
    for index, performed_item in enumerate(performed):
        if performed_item != available[index]:
            raise _MigrationError('migration order is corrupt')

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
            raise _MigrationError(
                'migration with provided name {} not found'.format(target)
            )
        migrations = migrations[:index + 1]

    return migrations


def _run(name, directory, direction):
    import_spec = import_util.spec_from_file_location(
        name,
        directory + name
    )
    module = import_util.module_from_spec(import_spec)
    import_spec.loader.exec_module(module)

    getattr(module, direction)()


def _set_state(direction, old_state, migrations, state_file):
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


class _MigrationError(Exception):
    def __init__(self, message, *args):
        super(_MigrationError, self).__init__(message, *args)
        self.message = message
