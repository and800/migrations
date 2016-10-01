Migrations
==========

Simple, cross-database migration tool for Python applications.
Inspired by `node migrations <https://github.com/tj/node-migrate>`_.

Status
------
The project is in beta now. Bugs and breaking changes may occur.

Requirements
------------
Only Python 3 is supported for now.

Installation
------------
.. code-block:: bash

    $ pip install migrations

Notice, this distribution provides package and executable
script named :code:`migrate`, so check if it does not mess with
existing packages/scripts. Generally, you should neither install
this tool globally, nor install several migration tools for one project.

Features
--------
TBD

Usage
-----
.. code-block::

    usage: migrate [options] [action]

    actions:
      up     [-h] [NAME|COUNT]   (default) perform COUNT migrations or till
                                 given NAME (by default perform all available)
      down   [-h] [NAME|COUNT]   revert COUNT migrations or till
                                 given NAME (by default revert one)
      create [-h]  NAME          create new migration file

      show   [-h]                print all migrations in chronological order

    options:
      -h, --help                 show this help message and exit
      -v, --version              show version and exit
      -d PATH, --migrations-dir PATH
                                 directory where migrations are stored
      -s PATH, --state-file PATH
                                 location of file which stores database state
      -t PATH, --template-file PATH
                                 location of template file for new migrations

Each migration file must define functions :code:`up()` and :code:`down()`
without required arguments.

Simple migration example:

.. code-block:: python

    import redis

    db = redis.Redis(host='localhost', port=6379)

    def up():
        db.rpush('used_libraries', 'migrations')

    def down():
        db.rpop('used_libraries', 'migrations')

A bit more complex example. Let's assume that in current
working directory we have module named :code:`db`, which contains
singleton object responsible for DB connection, for example
`PyMySQL <https://github.com/PyMySQL/PyMySQL>`_ Connection object.
Current working directory is the first place to be scanned for
modules to import.

.. code-block:: python

    from db import connection

    def manage_cursor(action):
        def wrap():
            with connection.cursor() as cursor:
                action(cursor)
            connection.commit()
        return wrap

    @manage_cursor
    def up(cursor):
        cursor.execute(
            "INSERT INTO used_libraries (`name`) VALUES ('migrations')"
        )

    @manage_cursor
    def down(cursor):
        cursor.execute(
            "DELETE FROM used_libraries WHERE `name`='migrations'"
        )
