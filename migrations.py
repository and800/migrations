import time
import os

migrations_dir = 'migration_scripts/'


def create(name):
    template = """\
def up():
    pass


def down():
    pass
"""
    os.makedirs(migrations_dir, 0o775, exist_ok=True)
    now = str(int(time.time()))
    filename = '{}_{}'.format(now, name.replace(' ', '_'))
    with open('{}{}.py'.format(migrations_dir, filename), 'w') as file:
        file.write(template)
