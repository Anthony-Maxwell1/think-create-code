processingjs gallery app
========================


Initial Setup
-------------

Use virtualenv to setup the initial runtime environment:

    cd Think.Create.Code
    virtualenv .virtualenv
    source .virtualenv/bin/activate

    (.virtualenv)$ cd processingjs/
    (.virtualenv)$ pip install -U -r requirements.txt
    (.virtualenv)$ ./manage.py migrate
    (.virtualenv)$ touch gallery/wsgi.py # restart wsgi daemon


Create Users
------------
Use the given fixture to load the users:

    (.virtualenv)$ ./manage.py loaddata fixtures/000_staff_users.json
    Installed 6 object(s) from 1 fixture(s)


Or use the django shell/console to create users.

    (.virtualenv)$ ./manage.py shell
    >>> from django.contrib.auth.models import User
    >>> jill = User.objects.create_user('jill', 'jill.vogel@adelaide.edu.au', 'l0c0gallery')


Create Artworks
---------------
Use the django shell/console to create artwork, authored by a user.

    (.virtualenv)$ ./manage.py shell
    >>> from django.contrib.auth.models import User
    >>> from artwork.models import Artwork
    >>> Artwork.objects.all()
    []
    >>> jill = User.objects.get(username='jill')
    >>> empty =Artwork.objects.create(title="Empty", code="", author=jill, shared=False)
    >>> Artwork.objects.all()
    [<Artwork: Empty>]


Test Coverage
-------------
Run the unit and integration tests, and get test coverage

    (.virtualenv)$ coverage run --include=./*  manage.py test
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
