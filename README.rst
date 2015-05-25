Sparrow
=======

Performance monitoring platform which allows running automated performance tests
on a given codebase.


Getting Started - Development
-----------------------------

Installing Tools and Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up a virtual environment. Virtualenvwrapper_ is highly recommended.

.. _Virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/

::

    mkvirtualenv sparrow

or

::

    mkproject sparrow

The development requirements are defined in the ``requirements`` folder. Note that
these are divided into separate requirements for production and local development.


Install development requirements with::

    pip install -r requirements/local.txt

Install additional dependencies::

    apt-get install chromium-chromedriver

Setting Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of keeping sensitive data like the project ``SECRET_KEY`` and
database connection strings in settings files, or worse, keeping them
in an unversioned ``local_settings`` module, we use environment
variables to store these bits of data.

If you're using virtualenvwrapper, a convenient place to define these
is in your ``postactivate`` script. Otherwise, they can go in e.g.
``~/bash_profile``.

The database connection is defined using a URL instead of separate parameters
for database name, password, etc. For PostgreSQL, the string will look like::

    postgresql://username:password@hostname:port/database

For SQLite, use::

    sqlite:////full/path/to/your/database/file.sqlite

You can use a tool like `this secret key generator`_ to generate
a ``SECRET_KEY``.

.. _this secret key generator: http://www.miniwebtool.com/django-secret-key-generator/

Here is a list of the required environment variables:

* SPARROW_DATABASE_URL

* SPARROW_SECRET_KEY

The following environment variables are required for test runner:

* SPARROW_RUNNER_DEPLOY_HOST

* SPARROW_RUNNER_TARGET_HOST

If you are using virtualenvwrapper, begin editing the ``postactivate`` script as follows::

    cdvirtualenv
    vim bin/postactivate

Set the contents as follows::

    #!/bin/bash
    # This hook is run after this virtualenv is activated.

    export SPARROW_DATABASE_URL="postgresql://username:password@hostname:port/database";
    export SPARROW_SECRET_KEY="";
    export DJANGO_SETTINGS_MODULE="sparrow.settings.local";
    export PYTHONPATH="/path/to/sparrow";

Setting ``DJANGO_SETTINGS_MODULE`` to ``sparrow.settings.local``,
is not strictly necessary, but helpful to avoid the need for the
``--settings`` flag to django management commands.

Similarly, setting ``PYTHONPATH`` lets you use ``django-admin.py`` instead of
``python manage.py``.


Running ``manage.py`` commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django's ``manage.py`` script is located in the ``apps`` directory. Any
``manage.py`` command can be run as follows::

    python apps/manage.py --settings=sparrow.settings.local COMMAND


**NOTE:** If you've set the ``DJANGO_SETTINGS_MODULE`` environment variable, and
set your ``PYTHONPATH``, you can omit the ``--settings=...`` portion of any
``manage.py`` commands, and substitute ``django-admin.py`` for ``manage.py``.
