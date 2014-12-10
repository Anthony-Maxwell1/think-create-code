Think.Create.Code
=================

Code and configuration related to the custom interactions created for the Think.Create.Code course.


Initial Setup
-------------

If you've just cloned this repo from git, you'll need to fetch the submodules:

    cd think-create-code
    git submodule init
    git submodule update


Use virtualenv to setup the initial runtime environment:

    cd think-create-code
    virtualenv .virtualenv
    source .virtualenv/bin/activate


Dependencies
------------

Dependent on the server configuration defined in adelaidex/course-units.git
