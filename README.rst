
Read It!
========

This started out life as a simple web app that solved a problem that I have
been experiencing.  I need a good way to keep track of the stuff on the web
that I have read.  The solution is obvious - write a web app in Python, host
it on Heroku, keep the data in MongoDB, and use some authentication scheme
that is based on a whitelist of allowed users.

Technology Stack
================

==================    ============================
Functionality         Component(s)
==================    ============================
Web Application       `flask`_
Test Environment      `unittest`_, `mock`_
Persistence           `pymongo`_
Authentication        `Flask-OpenID`_
Packaging             `setuptools`_, `pip`_
==================    ============================

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
    Ran 92 tests in 0.200s
    
    OK
    (env) readit$


Realistic Unit Testing
----------------------

A more realistic development environment, and the one that I use personally,
includes installing the `nose`_ and `coverage`_ packages and running
*nosetests* religiously.  This will ensure that additional code is at least
executed during the test process.  The tests should not take more than a
few seconds to execute and you get a *warm and fuzzy feeling* when the
"Missing" column is still empty at the end of the day::
    
    (env) readit$ nosetests
    ....................................................................
    Name                  Stmts   Miss  Cover   Missing
    ---------------------------------------------------
    readit                    7      0   100%   
    readit.flaskapp         141      0   100%   
    readit.helpers           42      0   100%   
    readit.json_support      54      0   100%   
    readit.mongo             54      0   100%   
    readit.reading           45      0   100%   
    readit.user              46      0   100%   
    ---------------------------------------------------
    TOTAL                   389      0   100%   
    ----------------------------------------------------------------------
    Ran 100 tests in 3.787s
    
    OK

Astute readers may have noticed that the number of tests executed between the
minimalistic environment and *nosetests* differs.  This is expected.  *Nose*
also executes the any defined `doctest`_ blocks.


Javascript Unit Testing
-----------------------

In addition to Python code, the application contains a bit of Javascript and
HTML that implements the browser-based interface.  Just like Python code,
Javascript requires testing or it feels shoddy to me.  After quite a bit of
playing around, I have settled on using the `QUnit`_ framework developed by
the same folk that brought us `jQuery`_.  I load both of them dynamically from
the appropriate CDNs so testing is easy.  Simply open */javascript/test.html*
in a web browser.  This will run a bunch of Unit Tests and present a nice
test report in your browser.  It should show a nice green bar that means
success.

The next step is to run a coverage tool on the Javascript code.  That took a
little more work but the `JSCover`_ tool was surprisingly easy to integrate
into the chain.  It requires that you have Java installed.  If you do, then
you can run the following command::
    
    (env) readit$ java -jar tools/JSCover-all.jar -ws --port=9001 \
        --document-root=javascript --report-dir=reports \
        --no-instrument=test --no-instrument=ext

Then point a web browser at http://localhost:9001/jscoverage.html?test.html
and you should be shown the QUnit page as a frame in the JSCover UI.  The
*Summary* tab will show you the breakdown of unit test coverage per Javascript
file.  The coverage report is saved off in the ``reports`` child of the
project root.

:todo: one day soon I will take the time to write a setup.py extension
   that automates this!


.. _flask: http://flask.pocoo.org/
.. _Flask-OpenID: http://packages.python.org/Flask-OpenID/
.. _mock: http://www.voidspace.org.uk/python/mock/
.. _pip: http://www.pip-installer.org/
.. _pymongo: http://api.mongodb.org/python/current/
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _unittest: http://docs.python.org/library/unittest.html#module-unittest
.. _virtualenv: http://www.virtualenv.org/
.. _nose: http://nose.readthedocs.org/
.. _coverage: http://nedbatchelder.com/code/coverage/
.. _doctest: http://docs.python.org/library/doctest.html
.. _QUnit: http://qunitjs.com/
.. _jQuery: http://jquery.com/
.. _JSCover: http://tntim96.github.com/JSCover/

