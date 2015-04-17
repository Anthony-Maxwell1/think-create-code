Think.Create.Code
-----------------

Code and configuration related to the custom interactions created for the
Think.Create.Code course.

code-reorder
============

JS Input problems testing student's ability to reorder lines of code to achieve
a target processingjs image.

Note: Because JS Input problems must exist in the course as static Files, the
components are not served directly by our servers.


processingjs
============

Django application which lets students create artworks using processingjs,
store them in our database, and share them with other students and the
general public, and get votes.

See processingjs/README.md for details on how to set up and modify the app.


processingjs/static/sandbox.html
================================

This is a ProcessingJS Sandbox which depends on many of the JS/CSS files in
processingjs/static, but can be used without running the Django application.
It can be embedded as an iframe in MyUni courses.
