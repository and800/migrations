from setuptools import setup

with open('README.rst', 'r') as file:
    readme = file.read()

setup(
    name='migrations',
    version='0.0.0.dev0',
    description='Yet another Python migration tool',
    long_description=readme,
    url='https://github.com/and800/migrations',
    author='Andriy Maletsky',
    author_email='andriy.maletsky@gmail.com',
    license='MIT',
    packages=['migrate'],
    entry_points=dict(
        console_scripts=['migrate = migrate.cli:entrypoint'],
    ),
)
