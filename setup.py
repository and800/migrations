from setuptools import setup

with open('README.rst', 'r') as file:
    readme = file.read()

with open('migrate/version.py', 'r') as file:
    version_str = file.read()
version_container = {}
exec(version_str, version_container)
version = version_container['__version__']

setup(
    name='migrations',
    version=version,
    description='Yet another Python migration tool',
    long_description=readme,
    url='https://github.com/and800/migrations',
    author='Andriy Maletsky',
    author_email='andriy.maletsky@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Version Control',
    ],
    keywords='migration',
    packages=['migrate'],
    entry_points=dict(
        console_scripts=['migrate = migrate.cli:entrypoint'],
    ),
)
