gallery redirect app
====================

This app redirects hits from the original Gallery applications to the new
consolidated app.


Initial Setup
-------------
Use virtualenv to setup the initial runtime environment:

    cd think-create-code/redirect
    virtualenv .virtualenv
    source .virtualenv/bin/activate

    (.virtualenv)$ pip install -U -r requirements.txt

Install apache app configuration:

    # Assumes this statement is in your apache config: Include conf.d/*._conf
    sudo cp etc/httpd/conf.d/10_processingjs._conf /etc/httpd/conf.d/
    sudo systemctl reload httpd
