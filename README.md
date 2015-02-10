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

If you've just cloned this repo from git, you'll need to fetch the submodules:

    cd think-create-code
    git submodule init
    git submodule update


Use virtualenv to setup the initial runtime environment:

    cd think-create-code
    virtualenv .virtualenv
    source .virtualenv/bin/activate

