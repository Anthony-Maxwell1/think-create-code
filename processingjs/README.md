processingjs gallery app
========================


Configuration
-------------
Create mysql database:

    mysql -u root -p < etc/sql/00_init.sql

Install apache app configuration:

    # Assumes this statement is in your apache config: Include conf.d/*._conf
    sudo cp etc/httpd/conf.d/10_processingjs._conf /etc/httpd/conf.d/
    sudo systemctl reload httpd



Initial Setup
-------------
Use virtualenv to setup the initial runtime environment:

    cd think-create-code
    virtualenv .virtualenv
    source .virtualenv/bin/activate

    (.virtualenv)$ cd processingjs/
    (.virtualenv)$ pip install --extra-index-url=https://lti-adx.adelaide.edu.au/pypi/ -U -r requirements.txt
    # selinux enforcing only
    (.virtualenv)$ sudo find ../.virtualenv/lib/python2.7/site-packages -name \*.so -exec chcon -t shlib_t {} \;

Initialise the database, using the appropriate DJANGO\_GALLERY\_ENVIRONMENT.

    (.virtualenv)$ DJANGO_GALLERY_ENVIRONMENT=development ./manage.py migrate
    (.virtualenv)$ touch gallery/wsgi.py # restart wsgi daemon


Initialise the database, using the appropriate DJANGO\_GALLERY\_ENVIRONMENT.

    (.virtualenv)$ DJANGO_GALLERY_ENVIRONMENT=development ./manage.py migrate
    (.virtualenv)$ touch gallery/wsgi.py  # restart wsgi daemon


Initial Data
------------
Use the data fixtures to load the initial staff users list:

    (.virtualenv)loco:processingjs$ DJANGO_GALLERY_ENVIRONMENT=development ./manage.py loaddata fixtures/000_staff_group.json
    Installed 1 object(s) from 1 fixture(s)


Development server
------------------
To run the development server, connecting to the configured development database:

    (.virtualenv)$ ./manage.py runserver 0.0.0.0:8000


Run tests
---------
To run the tests, using the flatfile test database:

    (.virtualenv)$ ./manage.py test

See below for information on integration tests and test coverage.


Create Users
------------

Use the django shell/console to create users.

    (.virtualenv)$ ./manage.py shell
    >>> from django_adelaidex.lti.models import User
    >>> jill = User.objects.create_user('jill', 'jill.vogel@adelaide.edu.au', 'password')


Create Artworks
---------------
Use the django shell/console to create artwork, authored by a user.

    (.virtualenv)$ ./manage.py shell
    >>> from django_adelaidex.lti.models import User
    >>> from artwork.models import Artwork
    >>> Artwork.objects.all()
    []
    >>> jill = User.objects.get(username='jill')
    >>> empty = Artwork.objects.create(title="Empty", code="", author=jill, shared=False)
    >>> Artwork.objects.all()
    [<Artwork: Empty>]


Test Coverage
-------------
Run the unit and integration tests, and get test coverage.

    (.virtualenv)$ coverage run --include=./* manage.py test
    (.virtualenv)$ coverage report
    Name               Stmts   Miss  Cover
    --------------------------------------
    gallery/__init__       0      0   100%
    gallery/settings      22      2    91%
    gallery/urls           5      0   100%
    artwork/__init__       0      0   100%
    artwork/models        18      0   100%
    artwork/tests        113      0   100%
    artwork/views         30      3    90%
    manage                 6      0   100%
    --------------------------------------
    TOTAL                194      5    97%


Integration Tests
-----------------
Integration tests are run using the selenium library, which requires a browser
to be installed.  We access this browser via an Xvfb session, configured to run
on display port :0, on address 0.0.0.0:8080.

    [root@loco ~]# sudo -u xvfb nohup /usr/bin/Xvfb :0 -screen 0 1024x768x24 &
