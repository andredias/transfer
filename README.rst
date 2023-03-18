Transfer File - Sharing Web Application in FastAPI
==================================================

``Transfer`` is file-sharing web application in FastAPI that allows users to upload and download files using a RESTful API.

This project is based on the `FastAPI minimum project template <https://github.com/andredias/perfect_python_project/tree/fastapi-minimum>`_.
It is heavily inspired by `Transfer.sh <https://transfer.sh/>`_,
which is implemented in Go.


Usage
=====

File Upload
-----------

To upload a file, use the following command pattern using HTTPie_:

.. code:: console

    $ http -f POST :5000 file@<filename>

The server returns a plain text response with the URL that should be used to download the file later.
The response URL format is ``http://localhost:5000/{token}/{filename}``.
It contains a random token and the filename of the uploaded file, so it is not possible to guess the URL of a file.

Upload example using HTTPie_:

.. code:: console

    $ http -f POST :5000 file@hypercorn.toml
    HTTP/1.1 201
    content-length: 48
    content-type: text/plain; charset=utf-8
    date: Sat, 18 Mar 2023 08:04:32 GMT
    location: http://localhost:5000/HZo7Y3pY_v8/hypercorn.toml
    server: hypercorn-h11

    http://localhost:5000/HZo7Y3pY_v8/hypercorn.toml

No authentication is required to upload files.
However, the server supports file sizes up to 5 MiB and the rate limit is 5 uploads per hour.
Also, the file will be automatically deleted after 1 hour.

File Download
-------------

To download a file, use the previously returned URL using the ``GET`` method:

.. code:: console

    $ http :5000/<token>/<filename>

Example:

.. code:: console

    $ http :5000/HZo7Y3pY_v8/hypercorn.toml
    HTTP/1.1 200
    content-length: 129
    content-type: text/plain; charset=utf-8
    date: Sat, 18 Mar 2023 08:05:14 GMT
    etag: adc28cc898b6726ed7007799d7d22f7e
    last-modified: Sat, 18 Mar 2023 08:04:32 GMT
    server: hypercorn-h11

    worker_class = "uvloop"
    bind = "0.0.0.0:5000"
    accesslog = "-"
    errorlog = "-"

There is no limit to the number of downloads and no authentication is required.


File Deletion
-------------

Files are automatically deleted after 1 hour.
However you can delete a file before the expiration time by using the ``DELETE`` method on the URL returned by the upload endpoint.

Example using HTTPie_:

.. code:: console

    $ http DELETE :5000/HZo7Y3pY_v8/hypercorn.toml
    HTTP/1.1 204
    content-type: application/json
    date: Sat, 18 Mar 2023 08:06:55 GMT
    server: hypercorn-h11

Anyone can delete the file. No authentication is required.



.. HTTPie: https://httpie.io/
