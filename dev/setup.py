from setuptools import setup

setup(
    name='migrations',
    entry_points=dict(
        console_scripts=['migrate = migrate.cli:entrypoint'],
    ),
)
