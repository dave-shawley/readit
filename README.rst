
Read It!
========

This started out life as a simple web app that solved a problem that I have
been experiencing.  I need a good way to keep track of the stuff on the web
that I have read.  The solution is obvious - write a web app in Python, host
it on Heroku, keep the data in MongoDB, and use some authentication scheme
that is based on a whitelist of allowed users.

Technology Stack
================

:Web Application: `flask`_
:Test Environment: `unittest`_, `mock`_
:Persistence: `pymongo`_
:Authentication: `Flask-OpenID`_
:Packaging: `setuptools`_, `pip`_

Development Tasks
=================

This section describes some of the common development tasks and the tools
that are used to accomplish them.

Initial Environment
-------------------

1. Pull source code from repository.

2. Setup a virtual environment using `virtualenv`_::

        readit$ virtualenv --no-site-packages --quiet env
        readit$ source env/bin/activate
        (env) readit$

3. Use *pip* to install the packages listed in *requirements.txt* as well as
   those in *dev-requirements.txt*::

        (env) readit$ pip install -r requirements.txt
        ... lots of output
        (env) readit$ pip install -r dev-requirements.txt
        ... lots more output

4. Run the tests to make sure everything is set up correctly::

        (env) readit$ nosetests

Minimal Test Environment
------------------------

You can run tests without installing *py.test* or *nose* though I would
highly recommend installing the latter.  You do need to install `mock`_
since the unit tests themselves depend on it.  Once you have *mock* installed,
you can run the unit tests using the `unittest`_ module directly::

    (env) readit$ python -m unittest tests
    .....................................................................
    -------------------------------------------------------------------------
    Ran 46 tests in 0.172s
    
    OK
    (env) readit$


.. _flask: http://flask.pocoo.org/
.. _Flask-OpenID: http://packages.python.org/Flask-OpenID/
.. _mock: http://www.voidspace.org.uk/python/mock/
.. _pip: http://www.pip-installer.org/
.. _pymongo: http://api.mongodb.org/python/current/
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _unittest: http://docs.python.org/library/unittest.html#module-unittest
.. _virtualenv: http://www.virtualenv.org/

