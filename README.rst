===================
Trace Python Client
===================


.. image:: https://img.shields.io/pypi/v/py-trace.svg
        :target: https://pypi.python.org/pypi/py-trace

.. image:: https://img.shields.io/travis/aiguofer/py-trace.svg
        :target: https://travis-ci.org/aiguofer/py-trace

.. image:: https://readthedocs.org/projects/py-trace/badge/?version=latest
        :target: https://py-trace.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



Python client for interacting with the Trace api. For information on the API see `the api documentation <http://developers.traceup.com/>`_


* Free software: MIT license
* Documentation: https://py-trace.readthedocs.io.


Getting Started
---------------

.. code-block:: python

    from py_trace import Trace

    client = Trace(<client_key>, <client_secret>)
    client.get_authorization_url()
    # output should be like https://www.alpinereplay.com/api/oauth_login?oauth_token=<token>, go to the url and authorize the app
    # after authorization, you should see a url like http://snow.traceup.com/api/oauth_login?oauth_token=<token>&oauth_verifier=<verifier>
    client.get_access_token(<verifier>)
    client.get_user()

To use in a web app (using a very basic Flask example):

.. code-block:: python

    from flask import Flask, request, redirect
    import json

    app = Flask(__name__)
    trace = Trace(<client_key>, <client_secret>, host + '/auth_callback')

    @app.route('/auth_callback')
    def handle_redirect():
        trace.get_access_token(request.args['oauth_verifier'])
        return redirect('/user')

    @app.route('/auth')
    def get_user_token():
        url = trace.get_auth_url()
        return redirect(url)

    @app.route('/user')
    def get_user():
        return json.dumps(trace.get_user())


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
