import time
import os
import json
import fnmatch

migrations_dir = 'migrations/'
state_file = migrations_dir + '.state.json'
state = None


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


# def perform(direction='up', name=None):
#     get_state()


def get_state():
    global state
    available = [
        file
        for file in os.listdir(migrations_dir)
        if fnmatch.fnmatch(file, '*.py')
    ]
    available.sort(key=lambda name: int(name.split('_', maxsplit=1)[0]))
    try:
        with open(state_file, 'r') as file:
            performed = json.load(file)
    except FileNotFoundError:
        performed = []
    state = [(file, file in performed) for file in available]


def set_state():
    with open(state_file, 'w') as file:
        json.dump(
            [name for name, performed in state if performed],
            file,
            indent=2
        )
