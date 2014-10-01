processingjs gallery app
========================


Create Users
------------

  (.virtualenv)$ cd processingjs
  (.virtualenv)$ ./manage.py shell
  >>> from django.contrib.auth.models import User
  >>> jill = User.objects.create_user('jill', 'jill.vogel@adelaide.edu.au', 'l0c0gallery')


Create Artworks
---------------

  (.virtualenv)$ cd processingjs
  (.virtualenv)$ ./manage.py shell
  >>> from django.contrib.auth.models import User
  >>> from artwork.models import Artwork
  >>> Artwork.objects.all()
  []
  >>> jill = User.objects.get(username='jill')
  >>> empty =Artwork.objects.create(title="Empty", code="", author=jill, shared=False)
  >>> Artwork.objects.all()
  [<Artwork: Empty>]
