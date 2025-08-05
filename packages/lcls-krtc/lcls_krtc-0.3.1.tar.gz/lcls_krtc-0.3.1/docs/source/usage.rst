krtc
====

This is a very small utility class for using Kerberos authentication with Python requests.

Installation
------------

With pip:

.. code:: bash

    $ pip install lcls-krtc

With conda:

.. code:: bash

    $ conda install -c conda-forge krtc

Example
-------

To use this when making calls to a web service:

.. code:: python

    import requests
    from krtc import KerberosTicket
    from urllib.parse import urlparse

    ws_url = "https://ws.slac.stanford.edu/ws/getData.json"
    krbheaders = KerberosTicket("HTTP@" + urlparse(ws_url).hostname).getAuthHeaders()
    r = requests.get(ws_url, headers=krbheaders)
    print(r.json())
